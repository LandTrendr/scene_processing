'''
This is a "conversion" batchfile template to handle zipped surface reflactance images.

It converts sr images into the correct format for LandTrendr 
segmentation by executing sr_handler functions.
'''
import os
import sys
from sr_handler import *

#INPUTS
proj_file_path = '/vol/v1/code/py/albers.txt'
targz_path = '/vol/v1/scenes/033029/tar_gz_files'
output_path = '/vol/v1/scenes/033029/images'
tmp_path = '/vol/v1/scenes/033029/images/tmp'

#call functions
#extract reflectance from ledaps hdf
processSR(targz_path, output_path, proj_file_path, tmp_path)

#create tc image for reflectance image
processLandtrendrTC(output_path)

#convert fmask to landtrendr mask
processFmask(targz_path, output_path, proj_file_path, tmp_path)
