#!/usr/bin/env python

#Edited by Tara Larrue 8/14/14 for scene_processing module
'''
Inputs: 
(1) scene number string [format: PPPRRR]
(2) scene path 
'''

#check masks against each other to find entirely masked out areas
#pixels are added together
import os, sys, glob, re, numpy, shutil
import numpy as np
from osgeo import ogr
from osgeo import gdal
from osgeo import gdalconst
from gdalconst import *
from shutil import *


def create_mask(sample, list, maskval=1):
	""" Create mask from GDALDataset if all band values equal to maskval """
    	#mask - array of masked out areas
	mask = np.zeros((sample.RasterYSize, sample.RasterXSize), dtype=np.uint8)

	#iterate through all of the masks, adding values together
	for cm in list:
		cmask = gdal.Open(cm, gdal.GA_ReadOnly)
		for b in range(sample.RasterCount):
			mask = mask + (cmask.GetRasterBand(b + 1).ReadAsArray() == maskval)
		cmask = None

	return (mask == sample.RasterCount).astype(np.uint8)



if 1 is 1:
	print sys.argv[1]
	scene = sys.argv[1]
	scenepath = sys.argv[2]
        
	useareaTopDir = os.environ['LT_USEAREA_MASKS']
	useareaPath = '{0}/{1}_usearea.bsq'.format(useareaTopDir,scene)
	print '\nUsearea Path is {0}'.format(useareaPath)
 
	#open and get bounding information from the cloudmask
	UA_image=gdal.Open(useareaPath, GA_ReadOnly)
	if UA_image is None:
		print("Failed to open "+UA_image)
		#return 1
	#Define extent
	UA_gt=UA_image.GetGeoTransform()
	ulx=UA_gt[0]
	uly=UA_gt[3]

	#the size of the use area file drives everything else
	masterXsize = UA_image.RasterXSize
	masterYsize = UA_image.RasterYSize

	#use that to figure out the lower right coordinate
	lrx=ulx+masterXsize*UA_gt[1]
	lry=uly+masterYsize*UA_gt[5]

        #set up output file for accumulating mask counts
        outcloud = os.path.join(scenepath, 'images/{0}_cumulative_mask.bsq'.format(scene))
	#use study area file as template
	#driver = UA_image.GetDriver()
	driver = gdal.GetDriverByName('ENVI')
	oc = driver.Create(outcloud, masterXsize, masterYsize, 1, gdalconst.GDT_Int16)
	oc.SetGeoTransform(UA_image.GetGeoTransform())
	oc.SetProjection(UA_image.GetProjection())
	

	#set up output image variable.  This will accumulate all of the 
	#  component cloudmasks
	countimage = np.zeros((masterYsize, masterXsize), dtype = np.uint8)


	#now find clouds
	cloudPaths = os.path.join(scenepath, 'images/[0-9][0-9][0-9][0-9]/*cloudmask.bsq')
	cloudList = sorted(glob.glob(cloudPaths))
	
	#First loop:  go through all cloud masks and find value

	for cloud in cloudList:
		print 'Working on {0}'.format(cloud)

		#get original cloud corners
		cloudfile=gdal.Open(cloud, gdal.GA_ReadOnly)
		cgt=cloudfile.GetGeoTransform()
		culx=cgt[0]
        	culy=cgt[3]
        	clrx=culx+cloudfile.RasterXSize*cgt[1]
        	clry=culy+cloudfile.RasterYSize*cgt[5]

		#figure out offset
		diffx=(ulx-culx)/cgt[1]	
		if diffx < 0:
			raise NotImplementedError('Cloud {0} ULX is within study area mask'.format(cloud))
		
		diffy=(uly-culy)/cgt[5]	
		
		if diffy < 0:
			raise NotImplementedError('Cloud {0} ULY is within study area mask'.format(cloud))

		#diffx and diffy are the number of pixels into the cloud mask where
		#   the study area mask begins
		#Since they are likely not integer, we need to nudge them
		#    By rounding, we essentially enact a nearest neighbor resample
		diffx=int(round(diffx))#need to make integer for subsetting commands later
		diffy=int(round(diffy))

		#check to make sure the lower right is not going to be offensive
		lorXoffset = diffx+masterXsize
		lorYoffset = diffy+masterYsize
		if lorXoffset > cloudfile.RasterXSize:
			raise NotImplementedError('Cloud {0} LORX is not large enough to accomodate study area'.format(cloud))
		if lorYoffset > cloudfile.RasterYSize:
			raise NotImplementedError('Cloud {0} LORY is not large enough to accomodate study area'.format(cloud))

		#now read in the cloud mask, using the appropriate size
		for b in range(cloudfile.RasterCount):
			image=cloudfile.GetRasterBand(b+1).ReadAsArray(diffx,diffy,masterXsize, masterYsize)#.astype(np.uint8)
			countimage=countimage+image

		#raise NotImplementedError('check image')


#write it out
percentimage = numpy.float64(countimage)/len(cloudList)*100
oc.GetRasterBand(1).WriteArray(percentimage)
oc = None
#raise NotImplementedError('check image')   


