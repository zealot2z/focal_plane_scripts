from __future__ import annotations
from pathlib import Path
from datetime import datetime, timedelta, timezone
import re
import numpy as np
import pandas as pd
import yaml
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, AltAz, EarthLocation
from photutils.segmentation import detect_sources, SourceCatalog

RAW_SHAPE = (1944, 2592)

def read_raw(path: str | Path, shape=RAW_SHAPE) -> np.ndarray:
    data = np.fromfile(path, dtype=np.uint8)
    return data.reshape(shape).astype(float)

def stretch_to_uint8(image: np.ndarray, pmin=1.0, pmax=99.7) -> np.ndarray:
    data = np.nan_to_num(image.astype(float), nan=0.0, posinf=0.0, neginf=0.0)
    lo, hi = np.percentile(data, [pmin, pmax])
    if hi <= lo:
        return np.zeros_like(data, dtype=np.uint8)
    scaled = np.clip((data - lo) / (hi - lo), 0, 1)
    return (255 * scaled).astype(np.uint8)

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def load_catalog(path):
    return pd.read_csv(path, sep=r'\s+', engine='python')

def load_tracking(path):
    df = pd.read_csv(path)
    ts = df['Timestamp'].astype(str)
    parsed = pd.to_datetime(ts, format='%Y-%m-%d_%H:%M:%S.%f', errors='coerce', utc=True)
    bad = parsed.isna()
    if bad.any():
        parsed2 = pd.to_datetime(ts[bad], format='%Y-%m-%d_%H:%M:%S', errors='coerce', utc=True)
        parsed.loc[bad] = parsed2
    if parsed.isna().any():
        badvals = ts[parsed.isna()].tolist()[:5]
        raise ValueError(f'Could not parse some tracking timestamps, e.g. {badvals}')
    df['Timestamp'] = parsed
    return df

def parse_local_timestamp_from_filename(filename, local_to_utc_hours=7.0):
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})-(\d{2}):(\d{2}):(\d{2})', filename)
    if not m:
        raise ValueError(f'Could not parse timestamp from {filename}')
    y, mo, d, hh, mm, ss = map(int, m.groups())
    local = datetime(y, mo, d, hh, mm, ss)
    utc = local + timedelta(hours=local_to_utc_hours)
    return utc.replace(tzinfo=timezone.utc)

def nearest_tracking_row(df, utc_dt):
    t = pd.Timestamp(utc_dt)
    idx = (df['Timestamp'] - t).abs().idxmin()
    return df.loc[idx]

def star_altaz(ra_deg, dec_deg, utc_dt, lat_deg, lon_deg, height_m):
    loc = EarthLocation(lat=lat_deg * u.deg, lon=lon_deg * u.deg, height=height_m * u.m)
    coord = SkyCoord(ra=ra_deg * u.deg, dec=dec_deg * u.deg, frame='icrs')
    aa = coord.transform_to(AltAz(obstime=Time(utc_dt), location=loc))
    return aa.az.deg, aa.alt.deg

def get_refined_centroids(image_data, expected_pts, threshold, search_radius=50):
    found_pts = []
    for exp_x, exp_y in expected_pts:
        x_min = max(0, int(exp_x - search_radius))
        x_max = min(image_data.shape[1], int(exp_x + search_radius))
        y_min = max(0, int(exp_y - search_radius))
        y_max = min(image_data.shape[0], int(exp_y + search_radius))
        crop = image_data[y_min:y_max, x_min:x_max]
        segm = detect_sources(crop, threshold, npixels=5)
        if segm is None:
            continue
        cat = SourceCatalog(crop, segm)
        obj = cat.to_table().to_pandas().nlargest(1, 'area')
        actual_x = float(obj['xcentroid'].values[0] + x_min)
        actual_y = float(obj['ycentroid'].values[0] + y_min)
        found_pts.append([actual_x, actual_y])
    return np.array(found_pts)

def affine_from_leds(master_leds, image, threshold, search_radius):
    import cv2
    pts_test = get_refined_centroids(image, master_leds, threshold, search_radius)
    if len(pts_test) < 4:
        raise RuntimeError(f'Only found {len(pts_test)} LEDs')
    n = min(len(master_leds), len(pts_test))
    M, _ = cv2.estimateAffinePartial2D(master_leds[:n], pts_test[:n])
    return M, pts_test

def transform_point(M, xy):
    x, y = xy
    return np.array([M[0,0]*x + M[0,1]*y + M[0,2], M[1,0]*x + M[1,1]*y + M[1,2]])

def sky_offset_to_pixel(delta_east_arcmin, delta_el_arcmin, alpha_deg, pix_per_arcmin):
    base = np.array([-delta_el_arcmin, -delta_east_arcmin]) * pix_per_arcmin
    a = np.deg2rad(alpha_deg)
    R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    return R @ base

def pix_per_arcmin(pix2mm, mm_per_arcmin):
    return  mm_per_arcmin / pix2mm #misleading labels; pix2mm = 0.482 mm/pixel
