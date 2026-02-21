#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Multi-panel figure bundle (.fig.zip) - container for Pltz panels."""

from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

__all__ = ["Figz"]

_MANIFEST = {"bundle_type": "FIGZ", "version": "1.0", "created_by": "figrecipe"}


class Figz:
    """Multi-panel figure bundle (.fig.zip).

    Manages a ZIP file containing:
        manifest.json  - bundle type declaration
        spec.json      - figure spec with panel list
        style.json     - figure dimensions and theme
        panels/        - .plt.zip panel bundles

    Example
    -------
    >>> figz = Figz.create("Figure1.fig.zip", "Figure1")
    >>> figz.add_panel("A", pltz_path)
    >>> figz.add_panel("B", pltz_bytes)
    """

    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            raise FileNotFoundError(f"Figz bundle not found: {self.path}")
        with zipfile.ZipFile(self.path, "r") as zf:
            namelist = zf.namelist()
            self.spec = (
                json.loads(zf.read("spec.json")) if "spec.json" in namelist else {}
            )
            self.style = (
                json.loads(zf.read("style.json")) if "style.json" in namelist else {}
            )
        self.panels: Dict[str, Dict] = {
            p["label"]: p for p in self.spec.get("panels", [])
        }

    @classmethod
    def create(
        cls,
        path: Union[str, Path],
        name: str,
        size_mm: Optional[Dict] = None,
    ) -> "Figz":
        """Create a new empty .fig.zip bundle.

        Parameters
        ----------
        path : str or Path
            Output path (should end in .fig.zip).
        name : str
            Figure name / ID.
        size_mm : dict, optional
            Canvas size e.g. {"width_mm": 170, "height_mm": 120}.

        Returns
        -------
        Figz
            Loaded Figz instance.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        spec = {
            "figure": {"id": name, "title": name, "caption": ""},
            "panels": [],
        }
        style = {
            "size": size_mm or {"width_mm": 170, "height_mm": 120},
            "background": "#ffffff",
            "theme": {"mode": "light"},
        }

        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", json.dumps(_MANIFEST, indent=2))
            zf.writestr("spec.json", json.dumps(spec, indent=2))
            zf.writestr("style.json", json.dumps(style, indent=2))

        return cls(path)

    def save(self) -> None:
        """Save spec/style changes back to bundle."""
        with zipfile.ZipFile(self.path, "r") as zf:
            entries = {name: zf.read(name) for name in zf.namelist()}

        entries["spec.json"] = json.dumps(self.spec, indent=2, default=str).encode()
        entries["style.json"] = json.dumps(self.style, indent=2, default=str).encode()

        tmp = Path(tempfile.mktemp(suffix=self.path.suffix))
        try:
            with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
                for name, data in entries.items():
                    zf.writestr(name, data)
            shutil.move(str(tmp), str(self.path))
        except Exception:
            if tmp.exists():
                tmp.unlink()
            raise

    def add_panel(
        self,
        label: str,
        pltz_source: Union[bytes, str, Path],
        position: Optional[Dict] = None,
        size: Optional[Dict] = None,
    ) -> None:
        """Add a .plt.zip panel to this figure.

        Parameters
        ----------
        label : str
            Panel label (e.g., "A", "B").
        pltz_source : bytes, str, or Path
            Panel bytes or path to a .plt.zip file.
        position : dict, optional
            Panel position e.g. {"x_mm": 5, "y_mm": 5}.
        size : dict, optional
            Panel size e.g. {"width_mm": 80, "height_mm": 68}.
        """
        if isinstance(pltz_source, (str, Path)):
            pltz_bytes = Path(pltz_source).read_bytes()
        else:
            pltz_bytes = pltz_source

        # Read all current entries
        with zipfile.ZipFile(self.path, "r") as zf:
            entries = {name: zf.read(name) for name in zf.namelist()}

        # Store panel bytes
        entries[f"panels/{label}.plt.zip"] = pltz_bytes

        # Update spec.panels
        if label not in self.panels:
            panel_info: Dict[str, Any] = {"label": label}
            if position:
                panel_info["position"] = position
            if size:
                panel_info["size"] = size
            self.panels[label] = panel_info
            self.spec["panels"] = list(self.panels.values())
        else:
            # Update position/size if provided
            if position:
                self.panels[label]["position"] = position
            if size:
                self.panels[label]["size"] = size
            self.spec["panels"] = list(self.panels.values())

        entries["spec.json"] = json.dumps(self.spec, indent=2, default=str).encode()

        # Rebuild ZIP atomically
        tmp = Path(tempfile.mktemp(suffix=self.path.suffix))
        try:
            with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
                for name, data in entries.items():
                    zf.writestr(name, data)
            shutil.move(str(tmp), str(self.path))
        except Exception:
            if tmp.exists():
                tmp.unlink()
            raise

    def add_panel_from_png(
        self,
        label: str,
        png_bytes: bytes,
        plot_type: str = "image",
        position: Optional[Dict] = None,
        size: Optional[Dict] = None,
    ) -> None:
        """Create a .plt.zip bundle from PNG bytes and embed it as a panel.

        Convenience wrapper around :meth:`add_panel` for the common case of
        adding a pre-rendered PNG image as a panel.

        Parameters
        ----------
        label : str
            Panel label (e.g., "A", "B").
        png_bytes : bytes
            PNG image data.
        plot_type : str, optional
            Plot type label stored in the panel's spec.json (default: "image").
        position : dict, optional
            Panel position e.g. {"x_mm": 5, "y_mm": 5}.
        size : dict, optional
            Panel size e.g. {"width_mm": 80, "height_mm": 68}.
        """
        from ._pltz import Pltz

        tmp = Path(tempfile.mktemp(suffix=".plt.zip"))
        try:
            Pltz.from_png(png_bytes, tmp, plot_type=plot_type)
            self.add_panel(label, tmp.read_bytes(), position, size)
        finally:
            if tmp.exists():
                tmp.unlink()

    def remove_panel(self, label: str) -> None:
        """Remove a panel (rebuilds ZIP).

        Parameters
        ----------
        label : str
            Panel label to remove.
        """
        panel_key = f"panels/{label}.plt.zip"
        with zipfile.ZipFile(self.path, "r") as zf:
            entries = {
                name: zf.read(name) for name in zf.namelist() if name != panel_key
            }

        self.panels.pop(label, None)
        self.spec["panels"] = list(self.panels.values())
        entries["spec.json"] = json.dumps(self.spec, indent=2, default=str).encode()

        tmp = Path(tempfile.mktemp(suffix=self.path.suffix))
        try:
            with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
                for name, data in entries.items():
                    zf.writestr(name, data)
            shutil.move(str(tmp), str(self.path))
        except Exception:
            if tmp.exists():
                tmp.unlink()
            raise

    def get_panel(self, label: str) -> "Pltz":
        """Extract panel as Pltz instance (via temp file).

        Note: The caller is responsible for cleaning up the temp file
        (accessible via the returned Pltz instance's .path attribute).

        Parameters
        ----------
        label : str
            Panel label.

        Returns
        -------
        Pltz
            Loaded Pltz instance for the panel.
        """
        from ._pltz import Pltz

        data = self.get_panel_pltz(label)
        if data is None:
            raise KeyError(f"Panel '{label}' not found in {self.path}")

        tmp = Path(tempfile.mktemp(suffix=".plt.zip"))
        tmp.write_bytes(data)
        return Pltz(tmp)

    def get_panel_pltz(self, panel_id: str) -> Optional[bytes]:
        """Get panel as raw bytes.

        Parameters
        ----------
        panel_id : str
            Panel label.

        Returns
        -------
        bytes or None
            Raw .plt.zip bytes, or None if panel not found.
        """
        panel_key = f"panels/{panel_id}.plt.zip"
        try:
            with zipfile.ZipFile(self.path, "r") as zf:
                if panel_key in zf.namelist():
                    return zf.read(panel_key)
        except Exception:
            pass
        return None

    def list_panel_ids(self) -> List[str]:
        """List panel labels in order.

        Returns
        -------
        list of str
            Panel labels.
        """
        return list(self.panels.keys())

    def get_panel_data(self, panel_id: str):
        """Get panel's CSV data as DataFrame.

        Parameters
        ----------
        panel_id : str
            Panel label.

        Returns
        -------
        DataFrame or None
        """
        import tempfile as _tempfile

        pltz_bytes = self.get_panel_pltz(panel_id)
        if pltz_bytes is None:
            return None

        from ._pltz import Pltz

        tmp = Path(_tempfile.mktemp(suffix=".plt.zip"))
        try:
            tmp.write_bytes(pltz_bytes)
            pltz = Pltz(tmp)
            return pltz.data
        finally:
            if tmp.exists():
                tmp.unlink()

    def render_preview(self) -> Optional[bytes]:
        """Return preview of first panel as PNG bytes.

        Returns
        -------
        bytes or None
        """
        panel_ids = self.list_panel_ids()
        if not panel_ids:
            return None

        from ._pltz import Pltz

        for pid in panel_ids:
            pltz_bytes = self.get_panel_pltz(pid)
            if pltz_bytes:
                tmp = Path(tempfile.mktemp(suffix=".plt.zip"))
                try:
                    tmp.write_bytes(pltz_bytes)
                    pltz = Pltz(tmp)
                    preview = pltz.get_preview() or pltz.render_preview()
                    if preview:
                        return preview
                finally:
                    if tmp.exists():
                        tmp.unlink()
        return None


# EOF
