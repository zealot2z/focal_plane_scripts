#!/usr/bin/env bash
set -euo pipefail

#INPUT_DIR="../images/focal_plane"
INPUT_DIR="/mnt/data/CTA/optics_data/20260423"
OUTDIR="./batch_outputs"
PATTERN="*.raw"
OVERWRITE=0
DO_PSF=0

ROWS=1944
COLS=2592
SOURCE_ID=2
HALFWIDTH=10
ZOOM_HALFWIDTH=100

usage() {
    cat <<USAGE
Usage:
  $0 [options]

Options:
  --input-dir DIR
  --outdir DIR
  --pattern GLOB
  --overwrite
  --do-psf
  -h, --help

Notes:
  PSF is skipped by default.
  Use --do-psf to run the PSF step.
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --input-dir) INPUT_DIR="$2"; shift 2 ;;
        --outdir) OUTDIR="$2"; shift 2 ;;
        --pattern) PATTERN="$2"; shift 2 ;;
        --overwrite) OVERWRITE=1; shift ;;
        --do-psf) DO_PSF=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
    esac
done

mkdir -p "$OUTDIR"

tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT

find "$INPUT_DIR" -maxdepth 1 -type f -name "$PATTERN" -print | sort > "$tmpfile"

if [[ ! -s "$tmpfile" ]]; then
    echo "No files matched pattern '$PATTERN' in $INPUT_DIR"
    exit 0
fi

while IFS= read -r rawfile; do
    fname=$(basename "$rawfile")
    ts=$(echo "$fname" | sed -E 's/.*-([0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}:[0-9]{2}:[0-9]{2})\.raw/\1/')

    if [[ ! "$ts" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}:[0-9]{2}:[0-9]{2}$ ]]; then
        echo "Skipping file with unrecognized timestamp format: $fname"
        continue
    fi

    prefix=$(echo "$ts" | sed 's/-/_/g; s/:/_/g')

    catalog="$OUTDIR/${prefix}_catalog.txt"
    preview="$OUTDIR/${prefix}_detections_stretched.png"
    preview_raw="$OUTDIR/${prefix}_detections_raw.png"
    jpg="$OUTDIR/${prefix}_stretched.jpg"
    raw_jpg="$OUTDIR/${prefix}_raw.jpg"
    psf_zoom="$OUTDIR/${prefix}_center_psf_zoom.png"
    psf_overlay="$OUTDIR/${prefix}_center_psf_overlay.png"

    echo "========================================"
    echo "Processing: $fname"

    need_process_raw=1
    need_psf=1

    if [[ $OVERWRITE -eq 0 ]]; then
        if [[ -f "$catalog" && -f "$preview" && -f "$preview_raw" && -f "$jpg" && -f "$raw_jpg" ]]; then
            need_process_raw=0
        fi
        if [[ -f "$psf_zoom" && -f "$psf_overlay" ]]; then
            need_psf=0
        fi
    fi

    if [[ $need_process_raw -eq 0 ]]; then
        echo "Skipping process_raw; outputs already exist"
    else
        echo "Processing raw: $rawfile"
        focal-plane-refactor process_raw "$rawfile"             --rows "$ROWS" --cols "$COLS"             --output-catalog "$catalog"             --preview "$preview"             --preview-raw "$preview_raw"             --dump-jpg "$jpg"             --dump-raw-jpg "$raw_jpg"
    fi

    if [[ $DO_PSF -eq 0 ]]; then
        echo "Skipping psf by default"
        continue
    fi

    if [[ ! -s "$catalog" ]]; then
        echo "Catalog missing or empty for PSF step: $catalog"
        echo "Skipping psf for $fname"
        continue
    fi

    if [[ $need_psf -eq 0 ]]; then
        echo "Skipping psf; outputs already exist"
        continue
    fi

    echo "Running PSF for: $rawfile"
    if ! focal-plane-refactor psf "$rawfile"         --rows "$ROWS" --cols "$COLS"         --catalog "$catalog"         --source-id "$SOURCE_ID"         --halfwidth "$HALFWIDTH"         --zoom-halfwidth "$ZOOM_HALFWIDTH"         --use-catalog-shape         --annotate-psf         --single-contour-2rms         --output-zoom "$psf_zoom"         --output-overlay "$psf_overlay"; then
        echo "WARNING: PSF failed for $fname"
        echo "Skipping bad image and continuing."
        rm -f "$psf_zoom" "$psf_overlay"
        continue
    fi
done < "$tmpfile"

echo "Done."
