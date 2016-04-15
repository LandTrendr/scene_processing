# sr_handler.py: convert sr tif images to
#   reflectance and cloud mask
#
# Author: Yang Z. & Tara Larrue (adapted from ledaps_handler.py)
# 
#
#********************************************************
import shutil
import os
import re
import sys
import glob
from numpy import *
import time
from osgeo import gdal
from osgeo import gdalconst
from datetime import datetime

try:
	GDAL_DATA= '"' + os.environ['GDAL_DATA'] + '"'
except KeyError:
	GDAL_DATA = '"/usr/lib/anaconda/share/gdal"'

def lt_basename(basename, appendix='ledaps.bsq', with_ts=True):
	"""convert ledaps name to landtrendr name convention

	SR_DIR: LT50330292011232-SC20160302202648
	LANDTRENDR: LT5033029_2011_232_20160407_224350_ledaps.bsq
	"""

	sensor = basename[0:3]	
	tsa = basename[3:9]
	year = basename[9:13]
	day = basename[13:16]
	ts = datetime.now().strftime('%Y%m%d_%H%M%S')
	
	if appendix and with_ts:
		return "_".join([sensor+tsa, year, day, ts, appendix]) 
	elif appendix:
		return "_".join([sensor+tsa, year, day, appendix]) 
	elif with_ts:
		return "_".join([sensor+tsa, year, day, ts]) 
	else:
		return "_".join([sensor+tsa, year, day]) 


def untar_to_tempdir(tar_file, tmp_path, untar=True):

	print("extracting " + tar_file)
	
	basefile =  os.path.basename(tar_file).replace('.tar.gz','')
	tmp_extract_dir = os.path.join(tmp_path, basefile)
	
	if untar:
	
		if not os.path.exists(tmp_extract_dir): 
			os.makedirs(tmp_extract_dir)
		else:
			if len([i for i in os.listdir(tmp_extract_dir) if i.endswith(".tif")]) >= 23:
				return tmp_extract_dir
			
		cmd = "tar -C {0} -zxvf {1}".format(tmp_extract_dir, tar_file)
		print cmd
		os.system(cmd)
	
	return tmp_extract_dir
	
def extract_tifs(sr_dir, output_path, proj_file):

	basedir = os.path.basename(sr_dir)
	print basedir
	
	#find image year information and make a year output folder
	image_year = basedir[9:13] #only known positioning so far...

	if image_year < 1984:
		import pdb; pdb.set_trace()
	print image_year
	
	#now process the hdf file
	this_outputdir = os.path.join(output_path, image_year) #ex./vol/v1/scenes/033033/image/1999/
	if not os.path.exists(this_outputdir):
		os.mkdir(this_outputdir)
        #import pdb; pdb.set_trace()
        
    #check if file has already been processed, return if it has
	check_this_refl = os.path.join(this_outputdir, lt_basename(basedir, '', False)+'*ledaps.bsq')
	files = glob.glob(check_this_refl)
	if len(files)>0: #file already been processed
		print "Skipping " + sr_dir
		print "Basename checked is"
		print lt_basename(basedir, '', False)
		return
	else:
		print "start processing"
	
	#if file has not been processed...	
	#tmp_path = temp_path
# 	ledaps_dir = os.path.dirname(hdf_file)
# 	if len(tmp_path)==0:
# 		tmp_path = os.path.join(ledaps_dir, "tmp")
# 		if not os.path.exists(tmp_path):
# 			os.mkdir(tmp_path)
	tmp_path = sr_dir
	
	refl_file = basedir + ".bsq"
	print(refl_file)
		
	tr_cmd = 'gdal_translate -of ENVI -a_nodata -9999 {0} {1}'
	
	#find surface reflectance bands within sr_dir
	bands = []
	for f in os.listdir(sr_dir):
		if f.endswith('.tif') and ('_sr_band' in f) and ('band6' not in f):
			this_file = f.replace('.tif','')[-5:] + ".bsq"
			print('creating ' + this_file + ' from ' + f + ' ...')
			dataset = os.path.join(sr_dir, f)
			os.system(tr_cmd.format(dataset, os.path.join(tmp_path, this_file)))
			bands.append(os.path.join(tmp_path, this_file))
	print(bands)
	
	#order bands
	band_numbers = [int(os.path.basename(i).split(".")[0][-1]) for i in bands]
	bands_ordered = [x for (y,x) in sorted(zip(band_numbers, bands))]
	
	merge_cmd = "gdal_merge.py -o {0} -of envi -separate -n -9999 {1}"
				
	print("stacking images to create " + refl_file)
	os_cmd = merge_cmd.format(os.path.join(tmp_path, refl_file), ' '.join(bands_ordered[0:6]))
	print(os_cmd)
	os.system(os_cmd)	
	
	#reproject to albers
	warp_cmd = 'gdalwarp -of ENVI -t_srs '+ proj_file +' -tr 30 30 -srcnodata "-9999 0" -dstnodata "-9999" {0} {1}'
	this_refl = lt_basename(basedir, 'ledaps.bsq')
	print("reprojecting to " + this_refl)
	os.system(warp_cmd.format(os.path.join(tmp_path, refl_file), os.path.join(this_outputdir, this_refl)))
	
	#remove temporary file
	#if (len(temp_path)==0):
	#shutil.rmtree(tmp_path)
	
	
	

def processSR(tsa_dir, output_path, proj_file, tmp_path=''):
	"""process all the surface reflectance files in the specified directory

		tsa_dir: input directory of SR tar files
		output_path: output directory for image stacks
		proj_file: projection definition file
		tmp_path: temporary processing directory
	"""
	
	failed = []
	for directory, dirnames, filenames in os.walk(tsa_dir):
		for f in filenames:
			if f.endswith('.tar.gz'): 
				this_file = os.path.join(directory, f)
				try:
					print("Processing " + this_file)
					this_sr_dir = untar_to_tempdir(this_file, tmp_path)
					extract_tifs(this_sr_dir, output_path, proj_file)
				except:
					#import pdb; pdb.set_trace()
					#print(sys.exc_info()[0])
					failed.append(this_file)
	print("\n\nThe following images failed:\n\n" + "\n".join(failed))
	
def create_ledaps_tc(refl_file, search):
	"""convert reflectance image to tasseled cap image"""


	brt_coeffs = [0.2043, 0.4158, 0.5524, 0.5741, 0.3124, 0.2303]
	grn_coeffs = [-0.1603, -0.2819, -0.4934, 0.7940, -0.0002, -0.1446]
	wet_coeffs = [0.0315, 0.2021, 0.3102, 0.1594,-0.6806, -0.6109]

	all_coeffs = [[brt_coeffs], [grn_coeffs], [wet_coeffs]]
	all_coeffs = matrix(array(all_coeffs))

	#create output image
	
	tc_file = refl_file.replace(search, '_tc.bsq')

	if os.path.exists(tc_file):
		print("Skipping " + refl_file)
		return 0

	#open qa file for readonly access
	dataset = gdal.Open(refl_file, gdalconst.GA_ReadOnly)
	if dataset is None:
		print("failed to open " + refl_file)
		return 1

	tc = dataset.GetDriver().Create(tc_file, dataset.RasterXSize, dataset.RasterYSize, 3, gdalconst.GDT_Int16)
	tc.SetGeoTransform(dataset.GetGeoTransform())
	tc.SetProjection(dataset.GetProjection())

	for y in range(dataset.RasterYSize):
		if (y+1) % 500 == 0:
			print "line " + str(y+1)
		refl = dataset.ReadAsArray(0, y, dataset.RasterXSize, 1)
		refl[refl==-9999] = 0
		tcvals = int16(all_coeffs * matrix(refl))

		tc.GetRasterBand(1).WriteArray(tcvals[0,:], 0, y)
		tc.GetRasterBand(2).WriteArray(tcvals[1,:], 0, y)
		tc.GetRasterBand(3).WriteArray(tcvals[2,:], 0, y)

	dataset = None
	tc = None

	
def processLandtrendrTC(img_dir, search='_ledaps.bsq'):
	"""process all reflectance image to tc
		by default assuming file ends with _ledaps.bsq
	"""
	failed = []
	for directory, dirnames, filenames in os.walk(img_dir):
		for f in filenames:
			
			if f.endswith(search): 
				this_file = os.path.join(directory, f)
				try:
					print("TC creation:Processing " + this_file)
					create_ledaps_tc(this_file, search)
				except:
					print(sys.exc_info()[0])
					failed.append(this_file)

	print("\n\nThe following images failed:\n\n" + "\n".join(failed))
	
def fmask_to_ltmask(fmask_dir, fmask, out_dir, proj_file):
	"""convert fmask to landtrendr cloud mask

		# FMASK:
		# clear land = 0
		# clear water = 1
		# cloud shadow = 2
		# snow = 3
		# cloud = 4
		# outside = 255
	"""
	basename = os.path.basename(fmask_dir)
	
	check_this_mask = os.path.join(out_dir, lt_basename(basename, '', False)+'*cloudmask.bsq')
	files = glob.glob(check_this_mask)
	if len(files)>0:
		print("skipping fmask")
		return 0

	this_mask = os.path.join(fmask_dir, fmask)
	ds_fmask = gdal.Open(this_mask, gdalconst.GA_ReadOnly)
	if ds_fmask is None:
		print("failed to open " + this_mask)
		return 1

	#LT5045029_1988_205_20120124_082324_cloudmask.bsq
	ltmask_base = lt_basename(basename, '')
	print(basename, ltmask_base)
	ltmask = os.path.join(out_dir, ltmask_base + '_raw.bsq')

	ds_ltmask = ds_fmask.GetDriver().Create(ltmask, ds_fmask.RasterXSize, ds_fmask.RasterYSize, 1, gdalconst.GDT_Byte)
	ds_ltmask.SetGeoTransform(ds_fmask.GetGeoTransform())
	ds_ltmask.SetProjection(ds_fmask.GetProjection())

	for y in range(ds_fmask.RasterYSize):
		if (y+1) % 500 == 0:
			print "line " + str(y+1)
		fm = ds_fmask.ReadAsArray(0, y, ds_fmask.RasterXSize, 1)
		lm = (fm < 255) + 0
		lm[fm==2] = 0 #shadow
		lm[fm==3] = 0 #snow
		lm[fm==4] = 0 #cloud

		ds_ltmask.GetRasterBand(1).WriteArray(lm, 0, y)
	ds_fmask = None
	ds_ltmask = None

	ltmask2 = os.path.join(out_dir, ltmask_base + '_cloudmask.bsq')

	#reproject to albers
	warp_cmd = 'gdalwarp -of ENVI -t_srs '+ proj_file +' -tr 30 30 --config GDAL_DATA {2} {0} {1}'
	os.system(warp_cmd.format(ltmask, ltmask2, GDAL_DATA))
	os.unlink(ltmask)
	#os.unlink(os.path.join(out_dir, ltmask_base + '_raw.hdr'))
	
	#remove temporary file if all required files have been generated for an image
	ltmask_base_notime = lt_basename(basename, '', False)
	req_endings = ["*cloudmask.bsq", "*tc.bsq", "*ledaps.bsq"]
	files_required = [os.path.join(out_dir, ltmask_base_notime+i) for i in req_endings]
	req_bools = map(lambda x: len(glob.glob(x))==1, files_required)
	
	if sum(req_bools) == 3:
		print "removing " + fmask_dir
		shutil.rmtree(fmask_dir)

	print "Done"
	
def processFmask(tsa_dir, out_dir, proj_file, tmp_path):
	"""Process all Fmask in tsa_dir to landtrendr mask"""
	
	failed = []
	for directory, dirnames, filenames in os.walk(tsa_dir):
		for f in filenames:
			if f.endswith('.tar.gz'): 
				this_file = os.path.join(directory, f)
				try:
					print("Processing " + this_file)
					
					
					this_sr_dir = untar_to_tempdir(this_file, tmp_path, untar=False)
					fmask_file = [i for i in os.listdir(this_sr_dir) if i.endswith('fmask.tif')][0]
				
					basename = os.path.basename(this_sr_dir)
					this_year = basename[9:13]
					this_output = os.path.join(out_dir, this_year)
				
					fmask_to_ltmask(this_sr_dir, fmask_file, this_output, proj_file)
				except:
					#import pdb; pdb.set_trace()
					#print(sys.exc_info()[0])
					failed.append(this_file)
	print("\n\nThe following images failed:\n\n" + "\n".join(failed))
	

	