Please see Qi Feng's...
1.) Refractor: https://github.com/qi-feng/focal_plane_refactor.git
2.) Overlay: https://github.com/qi-feng/focal_plane_overlay.git
For image processing. These scripts are modifications or tools to be used in tandem with refractor or overlay. 

#############################
MODELS
#############################

This folder contains three models, all in jupyter notebook format. When in the notebook, please upload a csv filled with your offset data so that the models may work. Beneath is a quick summary of each:

1.) ctattempt_bending - See Spengler, Gerrit et. all. “CTbend: A Bayesian open-source framework to model pointing corrections for Cherenkov telescopes.” arXiv, 12, July 2021, https://arxiv.org/pdf/2108.00720. 
This is the CTBend model in its most basic, trigonometric form. It is physically motivated and all parameters can be found in the paper attached. Within it are diagnostic plots for each parameter and scripts that plot data directly from the csv. 

2.) spherical bending (18 param dual coef, Azsin(E)) - This, and the 8 parameter model below, are mathematically motivated. They were derived using approximations of spherical harmonics. This 18 parameter model accounts for dipoles and quadrupoles, but may overfit with small datasets. 

3.) spherical_bending_(8_param_dual_coef,_Azsin(E)) This is the 8 parameter model. This model only accounts for dipoles and is best for when using small datasets. Like ctattempt, within it are diagnostic plots for each parameter and scripts that plot data directly from the csv.  

#############################
UTAHPHOTOS (GIT)
#############################

During my project, I used this folder to sort all outputs from the data pipeline (see Workflow.png for visual example). It contains several scripts that are useful for generating, plotting, and formatting data from csv files. Note that the scripts are the most important part of this folder. So long as your directories match the ones used in these scripts, the code should work. I am putting in this format mostly as convenience for the user and to get an idea for the layers of directories. Beneath is a summary of each: 

PNGtoPDF.py: Organizes and labels all .png (and other photo types) from a folder into a single PDF.

Data: Where the csv files are placed. Also where the data handling scripts are located that interact directly with said CSVs. Within this folder, we have... 
 -  plot2.py: Histograms and scatter plots to plot data from a .csv file. Very disorganized as of now, comment and uncomment plots you want to use.
 -  convertElAz.py: Converts RA and DEC of a star into azimuth and elevation.
 -  convertEquitorial.py: Converts a given El and Az of a star into RA and DEC. Meant to see how the calculated offset coordinates of a star compare to its true       RA and DEC. Option for either individual input (commented) or processing bulk amounts of coordinates. Timestamps, Elevation, and Azimuth must be provided from     data into their respective arrays.
 -  fits.py: Converts .png into .fits. May be useful for some generic background noise removal script.

Calibrations: This contains images of the focal plane's lattice, with a blue square around the center module and dot where the center is defined. If the center is well defined, the blue square should be along the edges of the center module and the center should be roughly in the middle. These images exist purely for visual verification that the center is well defined. 

Detections: This contains images of the stars/bright sources of light detected on the focal plane, where centroids have been placed around them. 

Overlayed: This contains images of a zoomed in overlay, where the offset vector and labels have been drawn. 

Nonzoom_overlayed: Exact same as Overlayed, but the images aren't zoomed in such that you may see the entire focal plane. 





cli.py: This is for cli for focal_plane_overlay, modified with autodetection that utilizes either the flux of the star pixels or the largest area centroid within
a certain area around the center of the mirror, defined in overlay_config for focal_plane_overlay. Also outputs a new calibration_square png such that one may more easily identify wether or not the center is well defined by examining the overlap between the lattice outline and the square itself, as well as the center cross' place within said square. 

run_pipeline.sh: This is a bash file, meant for reading all .raw files within a defined directory and processing them into .pngs. This script utilizes focal_plane_refractor and focal_plane_overlay. The directories will have to be modified for different users. Outputs a table of offsets such that data may be easily analyzed and plotted (using plot2.py). 

focal_plane_config.yml: Config file for focal_plane_refraction. The most important things within this file are the minarea and deblend_cont, as each control the number of centroids added to the catalog. A larger minarea and deblend_cont are reccomended, as each significantly lowers the amount of noise added to the catalog in the image. 

overlay_config.yml: Config file for focal_plane_overlay. The mirror center, optics details, LED Coordinates, and observer position (Fred-Lawrence-Whipple Observatory) are defined here. 

utils.py: Utilities for overlay cli and config. 




