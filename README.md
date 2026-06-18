cli.py: This is for cli for focal_plane_overlay, modified with autodetection that utilizes either the flux of the star pixels or the largest area centroid within
a certain area around the center of the mirror, defined in overlay_config for focal_plane_overlay.

run_pipeline.sh: This is a bash file, meant for reading all .raw files within a defined directory and processing them into .pngs. This script utilizes focal_plane_refractor and focal_plane_overlay. 
