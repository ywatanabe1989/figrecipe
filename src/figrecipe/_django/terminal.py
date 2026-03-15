#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Local terminal WebSocket server using pty.

Spawns a bash shell and bridges I/O over WebSocket.
Used by figrecipe's standalone GUI for the terminal panel.

Protocol:
  - Client sends raw text → written to pty master
  - Client sends "resize:ROWS:COLS" → pty resized via TIOCSWINSZ
  - Server sends raw text ← read from pty master
"""

import asyncio
import fcntl
import logging
import os
import pty
import struct
import termios
import threading

logger = logging.getLogger(__name__)


async def terminal_ws_handler(websocket, path=None):
    """Handle a single terminal WebSocket connection."""
    pid, master_fd = pty.fork()

    if pid == 0:
        # Child: exec bash
        env = os.environ.copy()
        env["TERM"] = "xterm-256color"
        os.execvpe("bash", ["bash", "--login"], env)

    # Parent: bridge master_fd <-> WebSocket
    flags = fcntl.fcntl(master_fd, fcntl.F_GETFL)
    fcntl.fcntl(master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    closed = False

    async def read_pty():
        while not closed:
            try:
                data = os.read(master_fd, 4096)
                if data:
                    await websocket.send(data.decode("utf-8", errors="replace"))
            except BlockingIOError:
                await asyncio.sleep(0.02)
            except OSError:
                break

    read_task = asyncio.create_task(read_pty())

    try:
        async for message in websocket:
            if isinstance(message, str):
                if message.startswith("resize:"):
                    parts = message.split(":")
                    if len(parts) == 3:
                        try:
                            rows, cols = int(parts[1]), int(parts[2])
                            winsize = struct.pack("HHHH", rows, cols, 0, 0)
                            fcntl.ioctl(master_fd, termios.TIOCSWINSZ, winsize)
                        except (ValueError, OSError):
                            pass
                else:
                    os.write(master_fd, message.encode("utf-8"))
            elif isinstance(message, bytes):
                os.write(master_fd, message)
    except Exception:
        pass
    finally:
        closed = True
        read_task.cancel()
        os.close(master_fd)
        try:
            os.kill(pid, 9)
            os.waitpid(pid, 0)
        except OSError:
            pass


def start_terminal_server(port: int = 5051):
    """Start standalone WebSocket terminal server."""
    try:
        import websockets
    except ImportError:
        logger.warning(
            "websockets package not installed. Terminal disabled. "
            "Install with: pip install websockets"
        )
        return None

    async def serve():
        async with websockets.serve(terminal_ws_handler, "127.0.0.1", port):
            logger.info("Terminal server on ws://127.0.0.1:%d", port)
            await asyncio.Future()

    thread = threading.Thread(target=lambda: asyncio.run(serve()), daemon=True)
    thread.start()
    return thread
