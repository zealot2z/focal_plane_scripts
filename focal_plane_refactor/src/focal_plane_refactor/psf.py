from __future__ import annotations

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse
from scipy.optimize import curve_fit

from .catalog import find_source_by_id, find_source_near, load_catalog
from .image_io import load_image, stretch_to_uint8
from .models import SourceDetection


@dataclass
class PSFFitResult:
    amplitude: float
    x0: float
    y0: float
    sigma_x: float
    sigma_y: float
    theta_deg: float
    offset: float
    fwhm_x: float
    fwhm_y: float


def _elliptical_gaussian(coords, amplitude, x0, y0, sigma_x, sigma_y, theta, offset):
    x, y = coords
    ct = np.cos(theta)
    st = np.sin(theta)
    xp = (x - x0) * ct + (y - y0) * st
    yp = -(x - x0) * st + (y - y0) * ct
    model = offset + amplitude * np.exp(-0.5 * ((xp / sigma_x) ** 2 + (yp / sigma_y) ** 2))
    return model.ravel()


def fit_psf_from_catalog(
    image_path: str,
    catalog_path: str,
    source_id: int | None = None,
    x_guess: float | None = None,
    y_guess: float | None = None,
    halfwidth: int = 50,
    shape: tuple[int, int] | None = None,
    pix2mm: float | None = None,
    fits_hdu: int = 0,
    max_match_radius: float = 50.0,
    use_catalog_shape: bool = False,
):
    image = load_image(image_path, shape=shape, fits_hdu=fits_hdu)
    catalog = load_catalog(catalog_path)

    if source_id is not None:
        src = find_source_by_id(catalog, source_id)
    elif x_guess is not None and y_guess is not None:
        src = find_source_near(catalog, x_guess, y_guess, max_radius=max_match_radius)
    else:
        raise ValueError("Provide either source_id or (x_guess, y_guess)")

    x0 = int(round(src.x))
    y0 = int(round(src.y))

    xmin = max(0, x0 - halfwidth)
    xmax = min(image.shape[1], x0 + halfwidth + 1)
    ymin = max(0, y0 - halfwidth)
    ymax = min(image.shape[0], y0 + halfwidth + 1)

    cutout = np.asarray(image[ymin:ymax, xmin:xmax], dtype=float)
    yy, xx = np.indices(cutout.shape)
    xx_full = xx + xmin
    yy_full = yy + ymin

    if use_catalog_shape and src.a_image is not None and src.b_image is not None:
        sigma_x0 = max(float(src.a_image), 1.0)
        sigma_y0 = max(float(src.b_image), 1.0)
        theta0 = np.deg2rad(float(src.theta_image or 0.0))
    else:
        sigma_x0 = max(cutout.shape[1] / 8.0, 1.0)
        sigma_y0 = max(cutout.shape[0] / 8.0, 1.0)
        theta0 = 0.0

    p0 = [
        float(cutout.max() - np.median(cutout)),
        float(src.x),
        float(src.y),
        sigma_x0,
        sigma_y0,
        theta0,
        float(np.median(cutout)),
    ]
    bounds = (
        [0.0, xmin, ymin, 0.5, 0.5, -np.pi / 2, -np.inf],
        [np.inf, xmax, ymax, halfwidth * 2.0, halfwidth * 2.0, np.pi / 2, np.inf],
    )

    popt, _pcov = curve_fit(
        _elliptical_gaussian,
        (xx_full, yy_full),
        cutout.ravel(),
        p0=p0,
        bounds=bounds,
        maxfev=20000,
    )

    amplitude, xfit, yfit, sigma_x, sigma_y, theta, offset = popt
    fit_image = _elliptical_gaussian((xx_full, yy_full), *popt).reshape(cutout.shape)

    fwhm_x = 2.354820045 * sigma_x
    fwhm_y = 2.354820045 * sigma_y

    result = PSFFitResult(
        amplitude=float(amplitude),
        x0=float(xfit),
        y0=float(yfit),
        sigma_x=float(sigma_x),
        sigma_y=float(sigma_y),
        theta_deg=float(np.rad2deg(theta)),
        offset=float(offset),
        fwhm_x=float(fwhm_x),
        fwhm_y=float(fwhm_y),
    )
    return result, cutout, fit_image, xmin, ymin, src


def plot_psf_zoom(
    image,
    result: PSFFitResult,
    fit_image,
    xmin: int,
    ymin: int,
    zoom_halfwidth: int = 20,
    annotate_psf: bool = False,
    single_contour_2rms: bool = False,
    contour_levels: int = 6,
    vmin: float | None = None,
    vmax: float | None = None,
):
    x0 = int(round(result.x0))
    y0 = int(round(result.y0))
    x1 = max(0, x0 - zoom_halfwidth)
    x2 = min(image.shape[1], x0 + zoom_halfwidth + 1)
    y1 = max(0, y0 - zoom_halfwidth)
    y2 = min(image.shape[0], y0 + zoom_halfwidth + 1)

    sub = np.asarray(image[y1:y2, x1:x2], dtype=float)
    yy, xx = np.indices(sub.shape)
    #xx += x1
    #yy += y1

    x0_local = result.x0 - x1
    y0_local = result.y0 - y1


    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(sub, origin="upper", cmap="viridis", vmin=vmin, vmax=vmax)
    plt.colorbar(im, ax=ax)

    model_sub = _elliptical_gaussian(
        (xx, yy),
        result.amplitude,
        #result.x0,
        #result.y0,
        x0_local,
        y0_local,
        result.sigma_x,
        result.sigma_y,
        np.deg2rad(result.theta_deg),
        result.offset,
    ).reshape(sub.shape)

    if single_contour_2rms:
        resid = sub - model_sub
        level = result.offset + 2.0 * np.std(resid)
        ax.contour(model_sub, levels=[level], colors="white", linewidths=1.5, origin="upper", extent=[x1, x2 - 1, y2 - 1, y1])
    else:
        levels = np.linspace(float(model_sub.min()), float(model_sub.max()), contour_levels + 2)[2:]
        ax.contour(model_sub, levels=levels, colors="white", linewidths=1.0, origin="upper", extent=[x1, x2 - 1, y2 - 1, y1])

    if annotate_psf:
        txt = (
            f"x={result.x0:.2f}, y={result.y0:.2f}\n"
            f"sigma_x={result.sigma_x:.2f} px\n"
            f"sigma_y={result.sigma_y:.2f} px\n"
            f"FWHM_x={result.fwhm_x:.2f} px\n"
            f"FWHM_y={result.fwhm_y:.2f} px\n"
            f"theta={result.theta_deg:.1f} deg"
        )
        ax.text(0.02, 0.98, txt, transform=ax.transAxes, va="top", ha="left", color="white", bbox=dict(boxstyle="round", facecolor="black", alpha=0.6))

    ax.set_title("PSF zoom")
    ax.set_xlabel("x [pix]")
    ax.set_ylabel("y [pix]")
    return fig


def plot_psf_overlay(
    image,
    result: PSFFitResult,
    fit_image,
    xmin: int,
    ymin: int,
    single_contour_2rms: bool = False,
    contour_levels: int = 6,
):
    img8 = stretch_to_uint8(image)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(img8, origin="upper", cmap="gray", vmin=0, vmax=255)

    h, w = fit_image.shape
    xx = np.arange(w) + xmin
    yy = np.arange(h) + ymin
    XX, YY = np.meshgrid(xx, yy)

    if single_contour_2rms:
        resid = image[ymin:ymin + h, xmin:xmin + w] - fit_image
        level = result.offset + 2.0 * np.std(resid)
        ax.contour(XX, YY, fit_image, levels=[level], colors="cyan", linewidths=1.8)
    else:
        levels = np.linspace(float(fit_image.min()), float(fit_image.max()), contour_levels + 2)[2:]
        ax.contour(XX, YY, fit_image, levels=levels, colors="cyan", linewidths=1.0)

    ell = Ellipse(
        (result.x0, result.y0),
        width=2.0 * result.sigma_x,
        height=2.0 * result.sigma_y,
        angle=result.theta_deg,
        fill=False,
        edgecolor="yellow",
        linewidth=1.5,
    )
    ax.add_patch(ell)
    ax.plot(result.x0, result.y0, marker="+", color="red", markersize=12, mew=2)
    ax.set_title("Full image with PSF contour")
    ax.set_xlabel("x [pix]")
    ax.set_ylabel("y [pix]")
    return fig
