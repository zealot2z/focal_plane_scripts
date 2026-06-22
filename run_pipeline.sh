#!/usr/bin/env bash
set -e

#NOTE: Please change user's name & pathways to focal_plane_refractor & focal_plane_overlay accordingly. 
#Also ensure that your environment name is matching the one used in this script, or change the script to match yours. 


##Input to process an image individually
#if [ -z "$1" ]; then
#    echo "Usage: ./run_pipeline.sh IMAGENAME.raw"
#    exit 1
#fi

#filename="$1"
#name="${filename%.raw}"
##individual input ends here

REFRACT_DIR="/c/Users/trist/focal_plane_refactor"
OVERLAY_DIR="/c/Users/trist/focal_plane_overlay"
FINAL_DIR="/c/Users/trist/UtahPhotos"
INPUT_SUBDIR="2026May"

shopt -s nullglob
files=("$REFRACT_DIR/$INPUT_SUBDIR"/*.raw)
total=${#files[@]}
source "$(conda info --base)/etc/profile.d/conda.sh"

if [ "$total" -eq 0 ]; then
    echo "No .raw files found."
    exit 1
fi

count=1

echo "Processing images..."
printf "Table of Processed Images:"
printf "\n%-20s  %8s %12s %12s\n"  "name" "count" "dEl (degree)" "dEast (degree)"
printf "%s\n" "-------------------------------------------------------------------"

#Begin processing; Process all files in directory at once
for filepath in "${files[@]}"; do
    filename="$(basename "$filepath")"
    name="${filename%.raw}"
    abbreviated="${name: -14}"
    BATCH_DIR="/c/Users/trist/UtahPhotos/$abbreviated"
    mkdir -p "$BATCH_DIR"

    #echo "[$count/$total] Processing: $name"

    #Step 1: Refraction
    conda activate frec
    cd "$REFRACT_DIR"

    python -m focal_plane_refactor.cli process_raw "./$INPUT_SUBDIR/$filename" \
        --rows 1944 \
        --cols 2592 \
        --output-catalog "${abbreviated}catalog.txt" \
        --preview-raw "${abbreviated}wLEDs_detections_raw.png" \
        --dump-raw-jpg "${abbreviated}wLEDs_raw.jpg" \
        --config focal_plane_config.yml

    mv "${abbreviated}wLEDs_detections_raw.png" "$BATCH_DIR/"
    mv "${abbreviated}wLEDs_raw.jpg" "$BATCH_DIR/"
    mv "${abbreviated}catalog.txt" "$OVERLAY_DIR/"

    #Step 2: Overlay
    conda activate fove
    cd "$OVERLAY_DIR"

    output=$(python -m focal_plane_overlay.cli "./$filename" \
        --catalog "./${abbreviated}catalog.txt" \
        --config overlay_config.yml \
        --led-threshold 150 \
        --led-search-radius 70 \
        --alpha-deg 0 \
        --offset-el-arcmin 0 \
        --offset-east-arcmin 0 \
        --ignore-skycam \
        --output "${abbreviated}overlay.png" \
        --zoom-output "${abbreviated}overlay_zoom.png" \
        --zoom-halfwidth 120 \
        --interactive-output "${abbreviated}overlay_interactive.html" \
        --calibration-output "${abbreviated}calibration_square.png" \
        --calibration-zoom-halfwidth 240
    )

    #generates table; for ease of data collecting; dEast & dEl are naturally in arcmin from cli
    line=$(echo "$output" | grep "dEast")
    dEast=$(echo "$line" | sed -E 's/.*dEast=([-0-9.]+).*/\1/')
    dEl=$(echo "$line" | sed -E 's/.*dEl=([-0-9.]+).*/\1/')
    dEast_deg=$(awk "BEGIN {print $dEast/60}")
    dEl_deg=$(awk "BEGIN {print $dEl/60}")
    printf "%-20s %8s %12.3f %12.3f\n" "$abbreviated" "[$count/$total]" "$dEl_deg" "$dEast_deg" 

    #Step 3: Outputs; copy before moving files
    mv "${abbreviated}catalog.txt" "$BATCH_DIR/"
    mv "${abbreviated}overlay.png" "$BATCH_DIR/"
    cp "${abbreviated}overlay_zoom.png" "$FINAL_DIR/Overlayed"
    mv "${abbreviated}overlay_zoom.png" "$BATCH_DIR/"
    cp "${abbreviated}calibration_square.png" "$FINAL_DIR/Calibrations"
    mv "${abbreviated}calibration_square.png" "$BATCH_DIR/"
    mv "${abbreviated}overlay_interactive.html" "$BATCH_DIR/"

    #echo "Done: $name"
    ((count++))

done

echo "Done: All Files Processed" 
