Please see Qi Feng's...
1.) Refractor: https://github.com/qi-feng/focal_plane_refactor.git
2.) Overlay: https://github.com/qi-feng/focal_plane_overlay.git
For image processing. These scripts are modifications or tools to be used in tandem with refractor or overlay. 


cli.py: This is for cli for focal_plane_overlay, modified with autodetection that utilizes either the flux of the star pixels or the largest area centroid within
a certain area around the center of the mirror, defined in overlay_config for focal_plane_overlay. Also outputs a new calibration_square png such that one may more easily identify wether or not the center is well defined by examining the overlap between the lattice outline and the square itself, as well as the center cross' place within said square. 

run_pipeline.sh: This is a bash file, meant for reading all .raw files within a defined directory and processing them into .pngs. This script utilizes focal_plane_refractor and focal_plane_overlay. The directories will have to be modified for different users. Outputs a table of offsets such that data may be easily analyzed and plotted (using plot2.py). 

overlay_config.yml: Config file for focal_plane_overlay. The mirror center, optics details, LED Coordinates, and observer position (Fred-Lawrence-Whipple Observatory) are defined here. 

utils.py: Utilities for overlay cli and config. 

plot2.py: Histograms and scatter plots to plot data from a .csv file. 

convertElAz.py: Converts RA and DEC of a star into azimuth and elevation.

convertEquitorial.py: Converts a given El and Az of a star into RA and DEC. Meant to see how the calculated offset coordinates of a star compare to its true RA and DEC. Option for either individual input (commented) or processing bulk amounts of coordinates. Timestamps, Elevation, and Azimuth must be provided from data into their respective arrays. 

fits.py: Converts .png into .fits for some generic background noise removal script. ##NEEDS WORK

PNGtoPDF.py: Organizes and labels all .png (and other photo types) from a folder into a single PDF.

