'''
This is a "conversion" batchfile template.

It converts ledaps outputs into the correct format for LandTrendr 
segmentation by executing ledaps_handler functions.
'''
import os
import sys
from ledaps_handler import *

#INPUTS
proj_file_path = '{{projectionPath}}'
ledaps_path = '{{ledapsPath}}'
output_path = '{{outputPath}}'
tmp_path = '{{tmpPath}}'

#call fucntions
#extract reflectance from ledaps hdf
processLedaps(ledaps_path, output_path, proj_file_path, tmp_path)

#create tc image for reflectance image
processLandtrendrTC(output_path)

#convert fmask to landtrendr mask
processFmask(ledaps_path, output_path, proj_file_path)

