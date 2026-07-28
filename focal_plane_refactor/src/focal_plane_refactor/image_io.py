from __future__ import annotations

from pathlib import Path

import numpy as np
from astropy.io import fits
from PIL import Image


def read_raw(path: str | Path, rows: int, cols: int, dtype=np.uint8) -> np.ndarray:
    arr = np.fromfile(path, dtype=dtype)
    expected = rows * cols
    if arr.size != expected:
        raise ValueError(f"RAW size mismatch: got {arr.size}, expected {expected}")
    return arr.reshape((rows, cols))


def load_image(path: str | Path, shape: tuple[int, int] | None = None, fits_hdu: int = 0) -> np.ndarray:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in {".fits", ".fit", ".fts"}:
        with fits.open(path) as hdul:
            data = hdul[fits_hdu].data
        if data is None:
            raise ValueError(f"No data found in FITS HDU {fits_hdu}: {path}")
        return np.asarray(data)
    if suffix == ".raw":
        if shape is None:
            raise ValueError("RAW input requires shape=(rows, cols)")
        rows, cols = shape
        return read_raw(path, rows=rows, cols=cols)
    img = Image.open(path)
    return np.asarray(img)


def _norm_to_uint8(image: np.ndarray, vmin: float, vmax: float) -> np.ndarray:
    arr = np.asarray(image, dtype=np.float32)
    if vmax <= vmin:
        return np.zeros_like(arr, dtype=np.uint8)
    arr = np.clip((arr - vmin) / (vmax - vmin), 0.0, 1.0)
    return np.asarray(255.0 * arr, dtype=np.uint8)


def stretch_to_uint8(image: np.ndarray, lo: float = 1.0, hi: float = 99.5) -> np.ndarray:
    arr = np.asarray(image, dtype=np.float32)
    vmin, vmax = np.percentile(arr, [lo, hi])
    return _norm_to_uint8(arr, float(vmin), float(vmax))


def linear_to_uint8(image: np.ndarray) -> np.ndarray:
    arr = np.asarray(image, dtype=np.float32)
    return _norm_to_uint8(arr, float(arr.min()), float(arr.max()))
