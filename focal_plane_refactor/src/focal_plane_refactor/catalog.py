from __future__ import annotations

from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError

from .models import SourceDetection

_OPTIONAL = {
    "A_IMAGE": "a_image",
    "B_IMAGE": "b_image",
    "THETA_IMAGE": "theta_image",
    "BACKGROUND": "background",
    "FLUX_ISO": "flux_iso",
}


def load_catalog(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Catalog file not found: {path}")
    if path.stat().st_size == 0:
        raise ValueError(f"Catalog file is empty: {path}")
    try:
        df = pd.read_csv(path, sep=r"\s+", engine="python", comment="#")
    except EmptyDataError as exc:
        raise ValueError(f"Catalog file has no columns/data: {path}") from exc
    for col in ["X_IMAGE", "Y_IMAGE"]:
        if col not in df.columns:
            raise ValueError(f"Catalog missing required column {col}")
    if df.empty:
        raise ValueError(f"Catalog contains no detections: {path}")
    return df


def save_catalog(df: pd.DataFrame, path: str | Path) -> None:
    df.to_csv(path, sep=" ", index=False, float_format="%.6f")


def source_from_row(row: pd.Series) -> SourceDetection:
    kwargs = {
        attr: float(row[col])
        for col, attr in _OPTIONAL.items()
        if col in row.index and pd.notna(row[col])
    }
    sid = int(row["ID"]) if "ID" in row.index and pd.notna(row["ID"]) else None
    return SourceDetection(source_id=sid, x=float(row["X_IMAGE"]), y=float(row["Y_IMAGE"]), **kwargs)


def find_source_near(df: pd.DataFrame, x: float, y: float, max_radius: float = 50.0) -> SourceDetection:
    d2 = (df["X_IMAGE"] - x) ** 2 + (df["Y_IMAGE"] - y) ** 2
    idx = d2.idxmin()
    dist = float(d2.loc[idx] ** 0.5)
    if dist > max_radius:
        raise ValueError(
            f"No catalog source found within {max_radius:.1f} pixels of ({x:.1f}, {y:.1f}). "
            f"Nearest source is {dist:.1f} pixels away."
        )
    return source_from_row(df.loc[idx])


def find_source_by_id(df: pd.DataFrame, source_id: int) -> SourceDetection:
    if "ID" not in df.columns:
        raise ValueError("Catalog does not contain an ID column")
    hits = df[df["ID"] == source_id]
    if hits.empty:
        raise ValueError(f"No catalog source found with ID={source_id}")
    return source_from_row(hits.iloc[0])
