from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG: dict[str, Any] = {
    "process_raw": {
        "method": "sep",
        "ellipse_scale": 2.0,
        "preview": None,
        "preview_raw": None,
        "dump_jpg": None,
        "dump_raw_jpg": None,
        "sextractor_path": None,
        "simple_detection": {
            "gaussian_sigma": 1.2,
            "percentile_threshold": 99.8,
            "sigma_threshold": 5.0,
            "opening_size": 2,
            "min_pixels": 2,
        },
        "sep": {
            "threshold_sigma": 5.0,
            "minarea": 3,
            "deblend_nthresh": 32,
            "deblend_cont": 0.005,
            "clean": True,
            "clean_param": 1.0,
            "bw": 64,
            "bh": 64,
            "fw": 3,
            "fh": 3,
        },
        "sewpy": {
            "params": [
                "X_IMAGE",
                "Y_IMAGE",
                "FLUX_ISO",
                "FLUX_MAX",
                "BACKGROUND",
                "A_IMAGE",
                "B_IMAGE",
                "THETA_IMAGE",
                "FLAGS",
            ],
            "config": {
                "DETECT_MINAREA": 3,
                "DETECT_THRESH": 5.0,
                "ANALYSIS_THRESH": 5.0,
                "FILTER": "Y",
                "DEBLEND_NTHRESH": 32,
                "DEBLEND_MINCONT": 0.005,
            },
        },
    },
    "psf": {
        "halfwidth": 50,
        "zoom_halfwidth": 20,
        "contour_levels": 6,
        "max_match_radius": 50.0,
        "pix2mm": None,
        "annotate_psf": False,
        "single_contour_2rms": False,
        "use_catalog_shape": False,
        "vmin": None,
        "vmax": None,
    },
}


def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def load_config(path: str | Path | None) -> dict[str, Any]:
    if path is None:
        return DEFAULT_CONFIG
    with open(path, "r", encoding="utf-8") as f:
        user_cfg = yaml.safe_load(f) or {}
    return _merge(DEFAULT_CONFIG, user_cfg)
