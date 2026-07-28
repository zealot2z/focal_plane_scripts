#!/usr/bin/env bash
set -euo pipefail

INPUT_DIR="/mnt/data/CTA/optics_data/20260423"
OUTDIR="./batch_outputs"
PATTERN="*.raw"
OVERWRITE=0
DO_PSF=0

ROWS=1944
COLS=2592

SOURCE_ID=""
PSF_X=""
PSF_Y=""
HALFWIDTH=80
ZOOM_HALFWIDTH=20

DETECT_MINAREA=8
DETECT_THRESH=8.0
ANALYSIS_THRESH=8.0
DEBLEND_NTHRESH=8
DEBLEND_MINCONT=0.1
FILTER="Y"

usage() {
    cat <<USAGE
Usage:
  $0 [options]

Options:
  --input-dir DIR
  --outdir DIR
  --pattern GLOB
  --rows N
  --cols N
  --overwrite
  --do-psf

  --source-id ID
  -p, --point X Y
  --halfwidth N
  --zoom-halfwidth N

  --detect-minarea N
  --detect-thresh X
  --analysis-thresh X
  --deblend-nthresh N
  --deblend-mincont X

  -h, --help
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --input-dir) INPUT_DIR="$2"; shift 2 ;;
        --outdir) OUTDIR="$2"; shift 2 ;;
        --pattern) PATTERN="$2"; shift 2 ;;
        --rows) ROWS="$2"; shift 2 ;;
        --cols) COLS="$2"; shift 2 ;;
        --overwrite) OVERWRITE=1; shift ;;
        --do-psf) DO_PSF=1; shift ;;

        --source-id) SOURCE_ID="$2"; shift 2 ;;
        -p|--point) PSF_X="$2"; PSF_Y="$3"; shift 3 ;;
        --halfwidth) HALFWIDTH="$2"; shift 2 ;;
        --zoom-halfwidth) ZOOM_HALFWIDTH="$2"; shift 2 ;;

        --detect-minarea) DETECT_MINAREA="$2"; shift 2 ;;
        --detect-thresh) DETECT_THRESH="$2"; shift 2 ;;
        --analysis-thresh) ANALYSIS_THRESH="$2"; shift 2 ;;
        --deblend-nthresh) DEBLEND_NTHRESH="$2"; shift 2 ;;
        --deblend-mincont) DEBLEND_MINCONT="$2"; shift 2 ;;

        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
    esac
done

if [[ $DO_PSF -eq 1 ]]; then
    if [[ -n "$SOURCE_ID" && ( -n "$PSF_X" || -n "$PSF_Y" ) ]]; then
        echo "Use either --source-id or -p/--point, not both." >&2
        exit 1
    fi
    if [[ -z "$SOURCE_ID" && ( -z "$PSF_X" || -z "$PSF_Y" ) ]]; then
        echo "For --do-psf, provide either --source-id ID or -p X Y." >&2
        exit 1
    fi
fi

mkdir -p "$OUTDIR"

CONFIG_YML="$OUTDIR/focal_plane_auto_config.yml"
cat > "$CONFIG_YML" <<EOF
process_raw:
  method: sewpy
  ellipse_scale: 2.0
  sewpy:
    params:
      - X_IMAGE
      - Y_IMAGE
      - FLUX_ISO
      - FLUX_MAX
      - BACKGROUND
      - A_IMAGE
      - B_IMAGE
      - THETA_IMAGE
      - FLAGS
    config:
      DETECT_MINAREA: ${DETECT_MINAREA}
      DETECT_THRESH: ${DETECT_THRESH}
      ANALYSIS_THRESH: ${ANALYSIS_THRESH}
      FILTER: ${FILTER}
      DEBLEND_NTHRESH: ${DEBLEND_NTHRESH}
      DEBLEND_MINCONT: ${DEBLEND_MINCONT}

psf:
  halfwidth: ${HALFWIDTH}
  zoom_halfwidth: ${ZOOM_HALFWIDTH}
  annotate_psf: true
  single_contour_2rms: true
EOF

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

    if [[ $need_process_raw -eq 1 ]]; then
        echo "Processing raw: $rawfile"
        focal-plane-refactor process_raw "$rawfile"             --rows "$ROWS" --cols "$COLS"             --config "$CONFIG_YML"             --output-catalog "$catalog"             --preview "$preview"             --preview-raw "$preview_raw"             --dump-jpg "$jpg"             --dump-raw-jpg "$raw_jpg"
    else
        echo "Skipping process_raw; outputs already exist"
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
    if [[ -n "$SOURCE_ID" ]]; then
        if ! focal-plane-refactor psf "$rawfile"             --rows "$ROWS" --cols "$COLS"             --catalog "$catalog"             --source-id "$SOURCE_ID"             --halfwidth "$HALFWIDTH"             --zoom-halfwidth "$ZOOM_HALFWIDTH"             --use-catalog-shape             --annotate-psf             --single-contour-2rms             --output-zoom "$psf_zoom"             --output-overlay "$psf_overlay"; then
            echo "WARNING: PSF failed for $fname"
            rm -f "$psf_zoom" "$psf_overlay"
            continue
        fi
    else
        if ! focal-plane-refactor psf "$rawfile"             --rows "$ROWS" --cols "$COLS"             --catalog "$catalog"             -p "$PSF_X" "$PSF_Y"             --halfwidth "$HALFWIDTH"             --zoom-halfwidth "$ZOOM_HALFWIDTH"             --use-catalog-shape             --annotate-psf             --single-contour-2rms             --output-zoom "$psf_zoom"             --output-overlay "$psf_overlay"; then
            echo "WARNING: PSF failed for $fname"
            rm -f "$psf_zoom" "$psf_overlay"
            continue
        fi
    fi
done < "$tmpfile"

echo "Done."
echo "Config used: $CONFIG_YML"
