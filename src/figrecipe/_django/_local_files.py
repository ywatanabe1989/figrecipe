#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Local filesystem adapter matching scitex-app's FilesBackend protocol.

Used as fallback when scitex-app is not installed or when running standalone.
Zero external dependencies — pure pathlib.
"""

import shutil
from pathlib import Path
from typing import List, Optional, Union


class LocalFilesAdapter:
    """FilesBackend-compatible adapter wrapping pathlib for local filesystem."""

    def __init__(self, root: Union[str, Path]):
        self._root = Path(root).resolve()

    def read(self, path: str, *, binary: bool = False) -> Union[str, bytes]:
        resolved = self._resolve(path)
        if not resolved.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if binary:
            return resolved.read_bytes()
        return resolved.read_text(errors="ignore")

    def write(self, path: str, content: Union[str, bytes]) -> None:
        resolved = self._resolve(path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            resolved.write_bytes(content)
        else:
            resolved.write_text(content)

    def list(
        self,
        directory: str = "",
        *,
        extensions: Optional[List[str]] = None,
    ) -> List[str]:
        target = self._resolve(directory) if directory else self._root
        if not target.is_dir():
            return []
        results = []
        for entry in sorted(target.iterdir(), key=lambda x: x.name.lower()):
            if entry.name.startswith("."):
                continue
            rel = str(entry.relative_to(self._root))
            if extensions:
                if entry.is_file() and entry.suffix.lower() in extensions:
                    results.append(rel)
                elif entry.is_dir():
                    results.append(rel)
            else:
                results.append(rel)
        return results

    def exists(self, path: str) -> bool:
        return self._resolve(path).exists()

    def delete(self, path: str) -> None:
        resolved = self._resolve(path)
        if not resolved.exists():
            raise FileNotFoundError(f"File not found: {path}")
        resolved.unlink()

    def rename(self, old_path: str, new_path: str) -> None:
        old = self._resolve(old_path)
        new = self._resolve(new_path)
        if not old.exists():
            raise FileNotFoundError(f"File not found: {old_path}")
        if new.exists():
            raise FileExistsError(f"File already exists: {new_path}")
        old.rename(new)

    def copy(self, src_path: str, dest_path: str) -> None:
        src = self._resolve(src_path)
        dest = self._resolve(dest_path)
        if not src.exists():
            raise FileNotFoundError(f"File not found: {src_path}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

    def _resolve(self, path: str) -> Path:
        resolved = (self._root / path.lstrip("/")).resolve()
        if not str(resolved).startswith(str(self._root)):
            raise ValueError(f"Path traversal detected: {path!r}")
        return resolved
