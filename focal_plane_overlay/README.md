# focal-plane-overlay

Overlay on a GRCCD raw image:
- LEDs found using engine.py-style local searches
- camera center from the LED affine transform
- selected catalog source ellipse
- true star Alt/Az from known RA/Dec
- positioner tracking point from nearest tracking RA/Dec row
- local +El and +East axes in image coordinates

## Run
```bash
python -m focal_plane_overlay.cli "The Imaging Source Europe GmbH-37514083-2592-1944-Mono8-2026-04-09-22:46:18.raw" \
  --catalog 2026_04_09_22_46_18_wLEDs_catalog.txt \
  --tracking skycam_data_20260409_7.txt \
  --config overlay_config.example.yml \
  --source-id 38 \
  --led-threshold 150 \
  --led-search-radius 70 \
  --alpha-deg 0 \
  --output overlay.png
```


## v2 fix
- tracking timestamps like `2026-04-10_05:03:29.504738` are now parsed correctly


## v3 additions
- robust tracking timestamp parsing
- extra cross for the **tracking-system predicted star position**
- optional deliberate offset support:
  - `pointing.offset_el_arcmin`
  - `pointing.offset_east_arcmin`
- if offset is nonzero, the white pointing arrow is drawn from the **offset star position** to the detected star
- if offset is zero, the white pointing arrow is drawn from the **tracking-system star position** to the detected star

Example with explicit offsets:
```bash
python -m focal_plane_overlay.cli "image.raw" \
  --catalog catalog.txt \
  --tracking skycam_data.txt \
  --config overlay_config.example.yml \
  --source-id 38 \
  --offset-el-arcmin 20 \
  --offset-east-arcmin -5 \
  --alpha-deg 0 \
  --output overlay.png
```


## v4 fixes
- corrected plate-scale conversion
- cleaner labels with corner info boxes
- prints pix_per_arcmin to stdout


## v5 fixes
- tracking RA/Dec is treated as the boresight/center sky position
- predicted star position is anchored at camera center, not the detected star
- commanded offset is subtracted from star-center separation before computing the white residual arrow
