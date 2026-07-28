from __future__ import annotations

import argparse

from .config import load_config
from .detect import process_raw
from .image_io import load_image
from .psf import fit_psf_from_catalog, plot_psf_overlay, plot_psf_zoom


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="focal-plane-refactor")
    subs = parser.add_subparsers(dest="command", required=True)

    p_raw = subs.add_parser("process_raw", help="Generate source catalog")
    p_raw.add_argument("image")
    p_raw.add_argument("--config", help="YAML config file")
    p_raw.add_argument("--output-catalog", required=True)
    p_raw.add_argument("--method", choices=["sep", "sewpy", "simple_detection"], default=None)
    p_raw.add_argument("--sextractor-path")
    p_raw.add_argument("--rows", type=int)
    p_raw.add_argument("--cols", type=int)
    p_raw.add_argument("--fits-hdu", type=int, default=0)
    p_raw.add_argument("--preview")
    p_raw.add_argument("--preview-raw")
    p_raw.add_argument("--dump-jpg")
    p_raw.add_argument("--dump-raw-jpg")

    p_psf = subs.add_parser("psf", help="Fit PSF from catalog target")
    p_psf.add_argument("image")
    p_psf.add_argument("--config", help="YAML config file")
    p_psf.add_argument("--catalog", required=True)
    g = p_psf.add_mutually_exclusive_group(required=True)
    g.add_argument("-p", "--point", nargs=2, type=float, metavar=("X", "Y"))
    g.add_argument("--source-id", type=int)
    p_psf.add_argument("--halfwidth", type=int, default=50)
    p_psf.add_argument("--zoom-halfwidth", type=int, default=20)
    p_psf.add_argument("--annotate-psf", action="store_true")
    p_psf.add_argument("--single-contour-2rms", action="store_true")
    p_psf.add_argument("--contour-levels", type=int, default=6)
    p_psf.add_argument("--max-match-radius", type=float, default=50.0)
    p_psf.add_argument("--pix2mm", type=float)
    p_psf.add_argument("--rows", type=int)
    p_psf.add_argument("--cols", type=int)
    p_psf.add_argument("--fits-hdu", type=int, default=0)
    p_psf.add_argument("--output-zoom", required=True)
    p_psf.add_argument("--output-overlay", required=True)
    p_psf.add_argument("--vmin", type=float, default=None, help="Colorbar lower limit for zoom image")
    p_psf.add_argument("--vmax", type=float, default=None, help="Colorbar upper limit for zoom image")
    p_psf.add_argument("--use-catalog-shape", action="store_true", help="Use catalog A_IMAGE/B_IMAGE/THETA_IMAGE for sigma instead of Gaussian fit")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    cfg = load_config(getattr(args, "config", None))
    shape = (args.rows, args.cols) if getattr(args, "rows", None) is not None and getattr(args, "cols", None) is not None else None

    if args.command == "process_raw":
        pr = cfg["process_raw"]
        process_raw(
            image_path=args.image,
            output_catalog=args.output_catalog,
            shape=shape,
            fits_hdu=args.fits_hdu,
            method=args.method or pr["method"],
            sextractor_path=args.sextractor_path or pr.get("sextractor_path"),
            preview_path=args.preview or pr.get("preview"),
            preview_raw_path=args.preview_raw or pr.get("preview_raw"),
            dump_jpg_path=args.dump_jpg or pr.get("dump_jpg"),
            dump_raw_jpg_path=args.dump_raw_jpg or pr.get("dump_raw_jpg"),
            ellipse_scale=float(pr.get("ellipse_scale", 2.0)),
            simple_detection_config=pr.get("simple_detection"),
            sep_config=pr.get("sep"),
            sewpy_params=pr.get("sewpy", {}).get("params"),
            sewpy_config=pr.get("sewpy", {}).get("config"),
        )
        return

    psf_cfg = cfg["psf"]
    kwargs = dict(
        image_path=args.image,
        catalog_path=args.catalog,
        source_id=args.source_id,
        halfwidth=args.halfwidth if args.halfwidth != 50 else psf_cfg["halfwidth"],
        shape=shape,
        pix2mm=args.pix2mm if args.pix2mm is not None else psf_cfg.get("pix2mm"),
        fits_hdu=args.fits_hdu,
        max_match_radius=args.max_match_radius if args.max_match_radius != 50.0 else psf_cfg["max_match_radius"],
        use_catalog_shape=args.use_catalog_shape or bool(psf_cfg.get("use_catalog_shape", False)),
    )
    if args.point is not None:
        kwargs["x_guess"], kwargs["y_guess"] = args.point

    result, cutout, fit_image, xmin, ymin, src = fit_psf_from_catalog(**kwargs)
    image = load_image(args.image, shape=shape, fits_hdu=args.fits_hdu)

    fig = plot_psf_zoom(
        image=image,
        result=result,
        fit_image=fit_image,
        xmin=xmin,
        ymin=ymin,
        zoom_halfwidth=args.zoom_halfwidth if args.zoom_halfwidth != 20 else psf_cfg["zoom_halfwidth"],
        annotate_psf=args.annotate_psf or bool(psf_cfg.get("annotate_psf", False)),
        single_contour_2rms=args.single_contour_2rms or bool(psf_cfg.get("single_contour_2rms", False)),
        contour_levels=args.contour_levels if args.contour_levels != 6 else psf_cfg["contour_levels"],
        vmin=args.vmin if args.vmin is not None else psf_cfg.get("vmin"),
        vmax=args.vmax if args.vmax is not None else psf_cfg.get("vmax"),
    )
    fig.savefig(args.output_zoom, dpi=150, bbox_inches="tight")

    fig2 = plot_psf_overlay(
        image=image,
        result=result,
        fit_image=fit_image,
        xmin=xmin,
        ymin=ymin,
        single_contour_2rms=args.single_contour_2rms or bool(psf_cfg.get("single_contour_2rms", False)),
        contour_levels=args.contour_levels if args.contour_levels != 6 else psf_cfg["contour_levels"],
    )
    fig2.savefig(args.output_overlay, dpi=150, bbox_inches="tight")

    print(f"Saved {args.output_zoom}")
    print(f"Saved {args.output_overlay}")
    print(f"Target source ID: {src.source_id}")
    print(f"Catalog position: x={src.x:.3f}, y={src.y:.3f}")


if __name__ == "__main__":
    main()
