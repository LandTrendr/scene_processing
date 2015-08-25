#********************************************************
# final.py: convert ledaps hdf4 image to
#   reflectance and cloud mask
#
# Author: Yang Z.
# Usage:  ledaps_hander_final.py targz_path, output_path, tmp_path, proj_file
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

def lt_basename(basename, appendix='_ledaps.bsq', with_ts=True):
	"""convert ledaps name to landtrendr name convention

	LEDAPS: lndsr.L71045029_02920070805
	LANDTRENDR: LE7045030_1999_195

	LEDAPS: lndsr.L5045029_02919840728
	LANDTRENDR: LT5045029_1984_210
	"""
	#import pdb ; pdb.set_trace()
	ts = ''
	if with_ts:
		"""
		OLD:ts = "_" + datetime.now().strftime('%Y%m%d_%H%M%S')
		"""
		ts = datetime.now().strftime('%Y%m%d_%H%M%S')


	if 'L7' in basename:
		baseyear = basename[21:23]
		basemonth = basename[23:25]
		baseday = basename[25:27]
		basedate=time.strptime(baseyear+" "+basemonth+" "+baseday, "%y %m %d")
		return "LE7"+basename[9:15]+'_'+basename[19:23]+'_'+str(basedate[7])+'_'+ts+appendix
	if 'WO' in basename:
                if 'LT5' in basename:
                        #lndsr.LT5045029008422650_WO.hdf

                        return "LT5"+basename[9:15]+'_19'+basename[17:19]+'_'+basename[19:22]+'_'+ts+appendix
                if 'LT4' in basename:
                        return "LT4"+basename[9:15]+'_19'+basename[17:19]+'_'+basename[19:22]+'_'+ts_appendix
	if 'L4' in basename:
		baseyear = basename[20:22]
		basemonth = basename[22:24]
		baseday = basename[24:26]
		basedate=time.strptime(baseyear+" "+basemonth+" "+baseday, "%y %m %d")
		return "LT4"+basename[8:14]+'_'+basename[18:22]+'_'+str(basedate[7])+'_'+ts+appendix
	if 'LE7' in basename:
		#lndsr.LE70450312012247EDC00.hdr  example -- seems to happen on 2012 images
		#we don't need to calculate the yearday, since it's in the file
		return "LE7"+basename[9:15]+'_'+basename[15:19]+'_'+basename[19:22]+'_'+ts+appendix
	if 'LT5' in basename:
		return "LT5"+basename[9:15]+'_'+basename[15:19]+'_'+basename[19:22]+'_'+ts+appendix
	if 'LT4' in basename:
		return "LT4"+basename[9:15]+'_'+basename[15:19]+'_'+basename[19:22]+'_'+ts+appendix
	else:
		baseyear = basename[20:22]
		basemonth = basename[22:24]
		baseday = basename[24:26]
		basedate=time.strptime(baseyear+" "+basemonth+" "+baseday, "%y %m %d")
		return "LT5"+basename[8:14]+'_'+basename[18:22]+'_'+str(basedate[7])+'_'+ts+appendix

def extract_hdf(hdf_file, output_path, proj_file, temp_path=''):
	print hdf_file
	#find image year information and make a year output folder
	basefile = os.path.basename(hdf_file).replace('hdr','')
	print basefile
	if 'L7' in basefile:
		image_year = basefile[19:23]
	elif 'WO' in basefile:
        
	        image_year = '19'+basefile[17:19]
	elif 'LE7' in basefile:
		image_year = basefile[15:19]
	elif 'LT5' in basefile:
		image_year = basefile[15:19]
	elif 'LT4' in basefile:
		image_year = basefile[15:19]
	else: 
		image_year = basefile[18:22]

	#if image_year > 2013:
	#	import pdb; pdb.set_trace() 
	if image_year < 1984:
		import pdb; pdb.set_trace()
	print image_year
	
	#now process the hdf file
	this_outputdir = os.path.join(output_path, image_year)
	if not os.path.exists(this_outputdir):
		os.mkdir(this_outputdir)
        #import pdb; pdb.set_trace()
	check_this_refl = os.path.join(this_outputdir, lt_basename(basefile, '', False)+'*ledaps.bsq')
	files = glob.glob(check_this_refl)
	if len(files)>0: #file already been processed
		print "Skipping " + hdf_file
		print "Basename checked is"
		print lt_basename(basefile, '', False)
		return
	else:
		print "start processing"

	tmp_path = temp_path
	ledaps_dir = os.path.dirname(hdf_file)
	if len(tmp_path)==0:
		tmp_path = os.path.join(ledaps_dir, "tmp")
		if not os.path.exists(tmp_path):
			os.mkdir(tmp_path)

	refl_file = os.path.basename(hdf_file).replace('.hdf', '.bsq')
	print(refl_file)

	cmd = "gdalinfo " + hdf_file
	tr_cmd = 'gdal_translate -of ENVI -a_nodata -9999 {0} {1}'
	f = os.popen(cmd)
	info = f.readlines()
	f.close()
	print "passed os.popen"
	bands = []
	for line in info:
		line = line.strip()
		mo = re.match("SUBDATASET_\d_NAME=", line)
		if mo:
			dataset = line.replace(mo.group(),'')
			this_file = dataset[-5:] + ".bsq"
			if (dataset[-5:].startswith("band") and dataset[-5:]!="band6"):
				print('creating ' + this_file + '...')
				os.system(tr_cmd.format(dataset, os.path.join(tmp_path, this_file)))
				bands.append(os.path.join(tmp_path, this_file))
	print(bands)

	merge_cmd = "gdal_merge.py -o {0} -of envi -separate -n -9999 {1}"

	# #now extract the refectance image
	print("stacking images to create " + refl_file)
	os.system(merge_cmd.format(os.path.join(tmp_path, refl_file), ' '.join(bands[0:6])))

	#reproject to albers
	warp_cmd = 'gdalwarp -of ENVI -t_srs '+ proj_file +' -tr 30 30 -srcnodata "-9999 0" -dstnodata "-9999" {0} {1}'
	this_refl = lt_basename(basefile, '_ledaps.bsq')
	print("reprojecting to " + this_refl)
	os.system(warp_cmd.format(os.path.join(tmp_path, refl_file), os.path.join(this_outputdir, this_refl)))

	#remove temporary file
	if (len(temp_path)==0):
		shutil.rmtree(tmp_path)

def processLedaps(tsa_dir, output_path, proj_file, tmp_path=''):
	"""process all the ledaps hdf files in the specified directory

		ledapsdir: input directory of hdf files
		output_path: output directory for image stacks
		proj_file: projection definition file
		tmp_path: temporary processing directory
	"""
	failed = []
	for directory, dirnames, filenames in os.walk(tsa_dir):
		for f in filenames:
			if f.endswith('.hdf') and f.startswith('lndsr'):
				this_file = os.path.join(directory, f)
				try:
					print("Processing " + this_file)
					extract_hdf(this_file, output_path, proj_file, tmp_path)
				except:
					import pdb; pdb.set_trace()
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
	check_this_mask = os.path.join(out_dir, basename[0:9] + '_' + basename[9:13] + '_' + basename[13:16] + '*_cloudmask.bsq')
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
	basename = os.path.basename(fmask_dir)
	ltmask_base = basename[0:9] + '_' + basename[9:13] + '_' + basename[13:16] + '_' + datetime.now().strftime('%Y%m%d_%H%M%S')
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
	warp_cmd = 'gdalwarp -of ENVI -t_srs '+ proj_file +' -tr 30 30 {0} {1}'
	os.system(warp_cmd.format(ltmask, ltmask2))
	os.unlink(ltmask)
	os.unlink(os.path.join(out_dir, ltmask_base + '_raw.hdr'))

	print "Done"

def processFmask(img_dir, out_dir, proj_file):
	"""Process all Fmask in img_dir to landtrendr mask"""
	failed = []
	for directory, dirnames, filenames in os.walk(img_dir):
		for f in filenames:
			if f.endswith('Fmask'):
				this_base = os.path.basename(directory)
				this_year = this_base[9:13]
				this_output = os.path.join(out_dir, this_year)
				if not os.path.exists(this_output):
					os.mkdir(this_output)
				try:
					print("Processing " + f)
					fmask_to_ltmask(directory, f, this_output, proj_file)
				except:
					print(sys.exc_info()[0])
					failed.append(os.path.join(directory, f))

	print("\n\nThe following images failed:\n\n" + "\n".join(failed))


