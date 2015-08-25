#!/usr/bin/env python

# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

import fnmatch
import os
import sys
import re
import glob

import numpy as np
from osgeo import gdal
from osgeo import gdal_array


'''
syntax for entry

python Fmask_fix.py PPPRRR path_to_scenes/PPPRRR

Options

-v - defines threshold

ex '-v 25' sets threshold for pixels that are masked out 75% of the time.
'''
#Edited by Tara Larrue 8/14/14 for scene_processing module

gdal.UseExceptions()
gdal.AllRegister()


params = sys.argv
assert re.match('[0-9][0-9][0-9][0-9][0-9][0-9]', params[1]), 'Invalid Scene Code'

scene = params[1]
root = params[2] 

def chooseFile(sceneCode, rootPath):
    '''Allows user to choose proper Fitted file
       if more than one matching filename present'''
    namePattern = '{0}_cumulative_mask.bsq'.format(scene)
    namePath = os.path.join(rootPath, 'images', namePattern)
    #namePattern = 'LT_v*_nbr_{0}_*_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]_fitted.bsq'.format(sceneCode)
    #namePath = os.path.join(rootPath, 'outputs/nbr', namePattern)
    
    fileList = glob.glob(namePath)

    if len(fileList) == 0:
        print 'No Fitted File Found'
        sys.exit()

    elif len(fileList) == 1:
        print os.path.basename(fileList[0])
        return fileList[0]
		
    else:
        fileDict = {}
        count = 0
        for foundFile in fileList:
            count += 1
            fileDict[str(count)] = foundFile
        print '\n\n'
        for f in sorted(fileDict.keys()):
            print '{0}: {1}'.format(f, os.path.basename(fileDict[f]))
        print '\n\n'
        answer = raw_input('Choose File: ')
        if answer not in fileDict.keys():
            print 'Invalid Entry'
            answer = raw_input('Choose File: ')
        else:
            selected = fileDict[answer]
        return selected
    

nbr_filename = chooseFile(scene, root)

maskPattern = 'L[TE][457]{0}_[0-9][0-9][0-9][0-9]_[0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]_cloudmask.bsq'.format(scene)
maskPath = os.path.join(root, 'images/[0-9][0-9][0-9][0-9]', maskPattern)
cloud_filenames = sorted(glob.glob(maskPath))

def create_mask(ds, maskval):
    """ Create mask from GDALDataset if all band values equal to maskval """
    mask = np.zeros((ds.RasterYSize, ds.RasterXSize), dtype=np.uint8)
    
    for b in range(ds.RasterCount):
        mask = mask + (ds.GetRasterBand(b + 1).ReadAsArray() <= maskval)
        
    return (mask == ds.RasterCount).astype(np.uint8)



def blank_mask(t_ds, s_ds, blankmask, test=False):
    """ Set target raster image to 1 where blankmask equal to 1 
    
    t_ds - target GDALDataset, an individual cloudmask
    s_ds - source dataset of blankmask, the nbr image
    blankmask - the raster to use
    """
    # Define target extent
    t_gt = t_ds.GetGeoTransform()
    t_ulx = t_gt[0]
    t_uly = t_gt[3]
    t_lrx = t_gt[0] + t_ds.RasterXSize * t_gt[1]
    t_lry = t_gt[3] + t_ds.RasterYSize * t_gt[5]
    
    # Source geotransform
    s_gt = s_ds.GetGeoTransform()
    
    # Setup target window
    tw_xoff = 0
    tw_yoff = 0
    tw_xsize = t_ds.RasterXSize
    tw_ysize = t_ds.RasterYSize

    # Compute source window in pixel coordinates
    ### NOTE: what to do with the resampling here?
    sw_xoff = int((t_ulx - s_gt[0]) / s_gt[1] + 0.1)
    sw_yoff = int((t_uly - s_gt[3]) / s_gt[5] + 0.1)
    sw_xsize = int((t_lrx - s_gt[0]) / s_gt[1] + 0.5) - sw_xoff
    sw_ysize = int((t_lry - s_gt[3]) / s_gt[5] + 0.5) - sw_yoff
    
    if sw_xoff < 0:
        tw_xoff = abs(sw_xoff)
        sw_xoff = 0
    if sw_yoff < 0:
        tw_yoff = abs(sw_yoff)
        sw_yoff = 0
    sw_xsize = min(sw_xsize, s_ds.RasterXSize)
    sw_ysize = min(sw_ysize, s_ds.RasterYSize)
    
    # Read in cloudmask image to be modified
    image = t_ds.GetRasterBand(1).ReadAsArray().astype(np.uint8)
    
    # Create new mask image from blankmask same size as image
    mask = np.zeros_like(image, dtype=np.uint8)
    mask[tw_yoff:(tw_yoff + sw_ysize), tw_xoff:(tw_xoff + sw_xsize)] = \
        blankmask[sw_yoff:sw_ysize, sw_xoff:sw_xsize]
    
    # Set places equal to 1 in "blankmask" to 1 in the cloudmask image
    image[np.where(mask == 1)] = 1
    
    if test is True:
        print 'Testing to see if mask was applied correctly'
        original = t_ds.GetRasterBand(1).ReadAsArray().astype(np.uint8)
        
        n_unmasked = np.where((mask == 1) & (original == 0))[0].size
        print 'Unmasked {n} pixels'.format(n=n_unmasked)
        
        n_before = np.where(original == 1)[0].size
        n_after = np.where(image == 1)[0].size
        
        print 'Unmasked pixels before: {n}'.format(n=n_before)
        print 'Unmasked pixels after: {n}'.format(n=n_after)
        
        assert n_unmasked == (n_after - n_before), 'Incorrect result!'
        
        print 'Test is successful!'
    
    return image


for cloud_filename in cloud_filenames:
    print 'Working on {0}'.format(cloud_filename)


    nbr_ds = gdal.Open(nbr_filename, gdal.GA_ReadOnly)
    cloud_ds = gdal.Open(cloud_filename, gdal.GA_ReadOnly)


    print 'NBR result'
    print 'x', nbr_ds.RasterXSize
    print 'y', nbr_ds.RasterYSize
    print 'b', nbr_ds.RasterCount
    print 'gt', nbr_ds.GetGeoTransform()

    print 'Cloudmask image'
    print 'x', cloud_ds.RasterXSize
    print 'y', cloud_ds.RasterYSize
    print 'b', cloud_ds.RasterCount
    print 'gt', cloud_ds.GetGeoTransform()

    if '-v' in params:
        valdex = params.index('-v')
        value = int(params[valdex+1])
    else:
        value = 0

    print '\nThreshold set to {0}%'.format(value)
    
    nbr_mask = create_mask(nbr_ds, value)

    new_mask = blank_mask(cloud_ds, nbr_ds, nbr_mask, test=True)
    # new_mask = blank_mask(cloud_ds, nbr_ds, nbr_mask)


    out_dir = os.path.join(root, 'images/repaired_masks')
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    driver = gdal.GetDriverByName('ENVI')

    out_ds = driver.Create(os.path.join(out_dir, '2fixed_' + os.path.basename(cloud_filename)),
                           cloud_ds.RasterXSize,
                           cloud_ds.RasterYSize,
                           1,
                           gdal_array.NumericTypeCodeToGDALTypeCode(new_mask.dtype.type))
    out_ds.GetRasterBand(1).SetNoDataValue(0)
    out_ds.GetRasterBand(1).WriteArray(new_mask)
    out_ds.SetGeoTransform(cloud_ds.GetGeoTransform())
    out_ds.SetProjection(cloud_ds.GetProjection())

    out_ds = None

    out_ds = driver.Create(os.path.join(out_dir, '2nbr_permamask.bsq'),
                           nbr_ds.RasterXSize,
                           nbr_ds.RasterYSize,
                           1,
                           gdal_array.NumericTypeCodeToGDALTypeCode(nbr_mask.dtype.type))
    out_ds.GetRasterBand(1).SetNoDataValue(0)
    out_ds.GetRasterBand(1).WriteArray(nbr_mask)
    out_ds.SetGeoTransform(nbr_ds.GetGeoTransform())
    out_ds.SetProjection(nbr_ds.GetProjection())

    out_ds = None

print 'Done!'

