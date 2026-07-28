from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import re

import numpy as np
import pandas as pd
import sep
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

from .catalog import save_catalog
from .image_io import load_image, linear_to_uint8, stretch_to_uint8

SEW_COLUMNS = [
    "X_IMAGE",
    "Y_IMAGE",
    "FLUX_ISO",
    "FLUX_MAX",
    "BACKGROUND",
    "A_IMAGE",
    "B_IMAGE",
    "THETA_IMAGE",
    "FLAGS",
]

CATALOG_COLUMNS = ["ID", *SEW_COLUMNS]


def _ensure_native_float32(image: np.ndarray) -> np.ndarray:
    arr = np.ascontiguousarray(np.asarray(image, dtype=np.float32))
    if not arr.dtype.isnative:
        arr = arr.byteswap().newbyteorder()
    return arr


def _simple_detection(image: np.ndarray, cfg: dict | None = None) -> pd.DataFrame:
    cfg = cfg or {}
    sigma = float(cfg.get("gaussian_sigma", 1.2))
    pct = float(cfg.get("percentile_threshold", 99.8))
    nsig = float(cfg.get("sigma_threshold", 5.0))
    opening_size = int(cfg.get("opening_size", 2))

    smooth = ndi.gaussian_filter(image.astype(float), sigma=sigma)
    threshold = max(np.percentile(smooth, pct), np.median(smooth) + nsig * np.std(smooth))
    mask = ndi.binary_opening(smooth > threshold, structure=np.ones((opening_size, opening_size)))
    labels, nlab = ndi.label(mask)

    rows = []
    for lab in range(1, nlab + 1):
        ys, xs = np.where(labels == lab)
        if len(xs) < int(cfg.get("min_pixels", 2)):
            continue

        vals = image[ys, xs].astype(float)
        flux = float(vals.sum())
        if flux <= 0:
            continue

        x0 = float((xs * vals).sum() / flux)
        y0 = float((ys * vals).sum() / flux)
        rows.append(
            {
                "ID": len(rows),
                "X_IMAGE": x0,
                "Y_IMAGE": y0,
                "FLUX_ISO": flux,
                "FLUX_MAX": float(vals.max()),
                "BACKGROUND": float(np.median(image)),
                "A_IMAGE": float(max(np.std(xs), 1.0)),
                "B_IMAGE": float(max(np.std(ys), 1.0)),
                "THETA_IMAGE": 0.0,
                "FLAGS": 0,
            }
        )

    return pd.DataFrame(rows, columns=CATALOG_COLUMNS)


def _sep_detection(image: np.ndarray, cfg: dict | None = None) -> pd.DataFrame:
    cfg = cfg or {}
    data = _ensure_native_float32(image)

    bkg = sep.Background(
        data,
        bw=int(cfg.get("bw", 64)),
        bh=int(cfg.get("bh", 64)),
        fw=int(cfg.get("fw", 3)),
        fh=int(cfg.get("fh", 3)),
    )
    data_sub = data - bkg

#default minarea was 3
    objects = sep.extract(
        data_sub,
        thresh=float(cfg.get("threshold_sigma", 5.0)),
        err=bkg.globalrms,
        minarea=int(cfg.get("minarea", 3)),
        deblend_nthresh=int(cfg.get("deblend_nthresh", 32)),
        deblend_cont=float(cfg.get("deblend_cont", 0.005)),
        clean=bool(cfg.get("clean", True)),
        clean_param=float(cfg.get("clean_param", 1.0)),
        segmentation_map=False,
    )

    rows = []
    for i, obj in enumerate(objects):
        rows.append(
            {
                "ID": i,
                "X_IMAGE": float(obj["x"]),
                "Y_IMAGE": float(obj["y"]),
                "FLUX_ISO": float(obj["flux"]),
                "FLUX_MAX": float(obj["peak"]),
                "BACKGROUND": float(bkg.globalback),
                "A_IMAGE": float(obj["a"]),
                "B_IMAGE": float(obj["b"]),
                "THETA_IMAGE": float(np.rad2deg(obj["theta"])),
                "FLAGS": int(obj["flag"]),
            }
        )

    df = pd.DataFrame(rows, columns=CATALOG_COLUMNS)
    if df.empty:
        return df
    df = df.sort_values("FLUX_MAX", ascending=False).reset_index(drop=True)
    df["ID"] = np.arange(len(df), dtype=int)
    return df


def _sewpy_detection(
    image_path: str | Path,
    sextractor_path: str | None = None,
    params: list[str] | None = None,
    sew_config: dict | None = None,
) -> pd.DataFrame:
    try:
        import sewpy  # type: ignore
    except Exception as exc:
        raise RuntimeError("sewpy is not installed") from exc

    executable = sextractor_path or shutil.which("source-extractor") or shutil.which("sex")
    if not executable:
        raise RuntimeError("No SExtractor executable found")

    raw_stem = Path(image_path).stem
    safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", raw_stem).replace(":", "_")

#Detect_minarea: 3 was default
    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        log_path = workdir / f"{safe_stem}.log.txt"
        sew = sewpy.SEW(
            workdir=str(workdir),
            sexpath=executable,
            params=params or SEW_COLUMNS,
            config=sew_config or {
                "DETECT_MINAREA": 3.0,
                "DETECT_THRESH": 5.0,
                "ANALYSIS_THRESH": 5.0,
                "FILTER": "Y",
                "DEBLEND_NTHRESH": 32,
                "DEBLEND_MINCONT": 0.005,
            },
            logfile=str(log_path),
        )
        out = sew(str(image_path))
        table = out["table"].to_pandas().copy()
        table.insert(0, "ID", np.arange(len(table), dtype=int))
        return table.reindex(columns=CATALOG_COLUMNS, fill_value=np.nan)


def _draw_overlay(base8: np.ndarray, df: pd.DataFrame, path: str | Path, ellipse_scale: float = 2.0) -> None:
    rgb = np.dstack([base8, base8, base8])
    im = Image.fromarray(rgb)
    draw = ImageDraw.Draw(im)

    for _, row in df.iterrows():
        x = float(row["X_IMAGE"])
        y = float(row["Y_IMAGE"])

        if all(c in row.index for c in ["A_IMAGE", "B_IMAGE", "THETA_IMAGE"]) and pd.notna(row["A_IMAGE"]) and pd.notna(row["B_IMAGE"]):
            a = max(float(row["A_IMAGE"]) * ellipse_scale, 2.0)
            b = max(float(row["B_IMAGE"]) * ellipse_scale, 2.0)
            th = np.deg2rad(float(row.get("THETA_IMAGE", 0.0)))
            pts = []
            for t in np.linspace(0, 2 * np.pi, 80):
                xr = a * np.cos(t)
                yr = b * np.sin(t)
                xp = x + xr * np.cos(th) - yr * np.sin(th)
                yp = y + xr * np.sin(th) + yr * np.cos(th)
                pts.append((xp, yp))
            draw.line(pts + [pts[0]], fill=(255, 0, 0), width=2)
        else:
            r = 5
            draw.ellipse((x - r, y - r, x + r, y + r), outline=(255, 0, 0), width=2)

        sid = int(row["ID"]) if "ID" in row.index and pd.notna(row["ID"]) else None
        if sid is not None:
            draw.text((x + 5, y + 5), str(sid), fill=(255, 255, 0))

    im.save(path)


def process_raw(
    image_path: str | Path,
    output_catalog: str | Path,
    shape: tuple[int, int] | None = None,
    fits_hdu: int = 0,
    method: str = "sep",
    sextractor_path: str | None = None,
    preview_path: str | Path | None = None,
    preview_raw_path: str | Path | None = None,
    dump_jpg_path: str | Path | None = None,
    dump_raw_jpg_path: str | Path | None = None,
    ellipse_scale: float = 2.0,
    simple_detection_config: dict | None = None,
    sep_config: dict | None = None,
    sewpy_params: list[str] | None = None,
    sewpy_config: dict | None = None,
) -> pd.DataFrame:
    image = load_image(image_path, shape=shape, fits_hdu=fits_hdu)

    if method == "sep":
        try:
            df = _sep_detection(image, cfg=sep_config)
        except Exception as exc:
            print(f"sep failed, default back to simple detection: {exc}")
            df = _simple_detection(image, cfg=simple_detection_config)
    elif method == "sewpy":
        try:
            df = _sewpy_detection(
                image_path,
                sextractor_path=sextractor_path,
                params=sewpy_params,
                sew_config=sewpy_config,
            )
        except Exception as exc:
            print(f"sewpy failed, default back to simple detection: {exc}")
            df = _simple_detection(image, cfg=simple_detection_config)
    elif method == "simple_detection":
        df = _simple_detection(image, cfg=simple_detection_config)
    else:
        raise ValueError(f"Unknown detection method: {method}")

    save_catalog(df, output_catalog)

    stretched = stretch_to_uint8(image)
    raw8 = linear_to_uint8(image)

    if dump_jpg_path:
        Image.fromarray(stretched).save(dump_jpg_path, quality=95)
    if dump_raw_jpg_path:
        Image.fromarray(raw8).save(dump_raw_jpg_path, quality=95)

    if preview_path:
        _draw_overlay(stretched, df, preview_path, ellipse_scale=ellipse_scale)
    if preview_raw_path:
        _draw_overlay(raw8, df, preview_raw_path, ellipse_scale=ellipse_scale)

    return df
