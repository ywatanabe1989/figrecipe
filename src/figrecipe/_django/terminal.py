#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Local terminal WebSocket server using pty.

Spawns a bash shell and bridges I/O over WebSocket.
Used by figrecipe's standalone GUI for the terminal panel.

Protocol:
  - Client sends raw text → written to pty
  - Client sends "resize:ROWS:COLS" → pty resized
  - Server sends raw text ← read from pty
"""

import asyncio
import fcntl
import logging
import os
import pty
import select
import struct
import termios
import threading

logger = logging.getLogger(__name__)

# Global pty state (one terminal per server process)
_pty_fd = None
_pty_pid = None
_clients: set = set()


def _spawn_pty():
    """Spawn a bash shell in a pty."""
    global _pty_fd, _pty_pid

    if _pty_fd is not None:
        return

    pid, fd = pty.openpty()
    _pty_pid = os.fork()

    if _pty_pid == 0:
        # Child process
        os.close(fd)
        os.setsid()

        # Open slave pty
        slave_fd = os.open(os.ttyname(pid), os.O_RDWR)
        os.dup2(slave_fd, 0)
        os.dup2(slave_fd, 1)
        os.dup2(slave_fd, 2)
        if slave_fd > 2:
            os.close(slave_fd)
        os.close(pid)

        env = os.environ.copy()
        env["TERM"] = "xterm-256color"

        os.execvpe("bash", ["bash", "--login"], env)
    else:
        # Parent process
        os.close(pid)
        _pty_fd = fd

        # Set non-blocking
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)


def _resize_pty(rows: int, cols: int):
    """Resize the pty."""
    if _pty_fd is None:
        return
    try:
        winsize = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(_pty_fd, termios.TIOCSWINSZ, winsize)
    except OSError:
        pass


def _read_pty() -> bytes:
    """Non-blocking read from pty."""
    if _pty_fd is None:
        return b""
    try:
        r, _, _ = select.select([_pty_fd], [], [], 0.01)
        if r:
            return os.read(_pty_fd, 4096)
    except (OSError, ValueError):
        pass
    return b""


def _write_pty(data: bytes):
    """Write to pty."""
    if _pty_fd is None:
        return
    try:
        os.write(_pty_fd, data)
    except OSError:
        pass


async def terminal_ws_handler(websocket, path=None):
    """WebSocket handler for terminal connections.

    Works with both websockets library and Django Channels.
    """
    _spawn_pty()
    _clients.add(websocket)

    # Read loop: pty → WebSocket
    async def read_loop():
        while True:
            data = await asyncio.get_event_loop().run_in_executor(None, _read_pty)
            if data:
                try:
                    await websocket.send(data.decode("utf-8", errors="replace"))
                except Exception:
                    break
            await asyncio.sleep(0.01)

    read_task = asyncio.create_task(read_loop())

    try:
        async for message in websocket:
            if isinstance(message, str):
                if message.startswith("resize:"):
                    parts = message.split(":")
                    if len(parts) == 3:
                        try:
                            rows = int(parts[1])
                            cols = int(parts[2])
                            _resize_pty(rows, cols)
                        except ValueError:
                            pass
                else:
                    _write_pty(message.encode("utf-8"))
            elif isinstance(message, bytes):
                _write_pty(message)
    finally:
        read_task.cancel()
        _clients.discard(websocket)


def start_terminal_server(port: int = 5051):
    """Start standalone WebSocket terminal server.

    For use when running figrecipe GUI standalone.
    """
    try:
        import websockets
    except ImportError:
        logger.warning(
            "websockets package not installed. "
            "Terminal disabled. Install with: pip install websockets"
        )
        return

    async def serve():
        async with websockets.serve(terminal_ws_handler, "127.0.0.1", port):
            logger.info("Terminal WebSocket server on ws://127.0.0.1:%d", port)
            await asyncio.Future()  # run forever

    thread = threading.Thread(target=lambda: asyncio.run(serve()), daemon=True)
    thread.start()
    return thread
