from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SourceDetection:
    source_id: int | None
    x: float
    y: float
    a_image: float | None = None
    b_image: float | None = None
    theta_image: float | None = None
    background: float | None = None
    flux_iso: float | None = None
