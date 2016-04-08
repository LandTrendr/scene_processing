#!/net/usr/local/bin/python
import sys
sys.path.append("/projectnb/trenders/code/py/")
from ledaps_handler import *

ledaps_path = '/projectnb/trenders/scenes/033033/P033-R033'
output_path = '/projectnb/trenders/scenes/033033/images'
proj_file_path = '/projectnb/trenders/code/py/albers.txt'
tmp_path = '/projectnb/trenders/scenes/033033/images/tmp'


#extract reflectance from ledaps hdf

processLedaps(ledaps_path, output_path, proj_file_path, tmp_path)


#create tc image for reflectance image
processLandtrendrTC(output_path)

#convert fmask to landtrendr mask
processFmask(ledaps_path, output_path, proj_file_path)
