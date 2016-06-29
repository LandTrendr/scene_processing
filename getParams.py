'''
Title: getParams.py
Author: Tara Larrue (tlarrue2991@gmail.com)

This python module contains scene processing functions to get batchfile parameters
'''
import os, sys
import glob

HELPERFILES = "/vol/v1/general_files/helperfiles"
PROJECTIONS = "/vol/v1/general_files/projections"
USEAREAS = "/vol/v1/scenes/gnn_snapped_cmon_usearea_files"

class globalParams:
    templateHdr = os.path.join(HELPERFILES, "mrlc_template_headerfile.hdr")

def find_diag_mask_files(sceneDir,process):
    '''This function locates diag.sav and mask files for LandTrendr labelling & history variables processes'''   
    outputDir = os.path.join(sceneDir,"outputs")
    
    #determine type of segmentation run output
    nbr = ["lab_mr224", "lab_mr227", "lab_nbr", "lab_nccn", "hist_nomask", "hist_plusmask"]
    wetness = ["lab_mr224_w", "lab_mr227_w", "hist_w", "hist_w_nomask"]
    band5 = ["lab_band5", "hist_band5_nomask"]
    if process in nbr:
        outputType = "nbr"
    elif process in wetness:
        outputType = "wetness"
    elif process in band5:
        outputType = "band5"
    else:
        sys.exit("ERROR: Process is not valid. Process step choices: {0}".format(nbr+wetness+band5))
    
    #if process requires a mask file, locate it  
    maskNeeded = ["hist_plusmask", "hist_w"]  
    if process in maskNeeded:
        try: #find correct lt_labels directory 1st, then looks inside for mask file. [dependent on naming conventions!]
            labelsDir = glob.glob(os.path.join(outputDir,outputType,"{0}_lt_labels*".format(outputType)))[0]
            maskFile = glob.glob(os.path.join(labelsDir,"*_greatest_recovery_mmu11_loose.bsq"))[0]
        except:
            sys.exit("ERROR: Cannot find mask file. Please check label outputs.")
    else:
        maskFile = None     
    
    #find base diag file by deducing from glob sets
    allDiags = glob.glob(os.path.join(outputDir,outputType,"*diag.sav*"))
    exDiags = glob.glob(os.path.join(outputDir,outputType,"*ftv_diag.sav*"))
    try:
        diagFile = list(set(allDiags)-set(exDiags))[0]
    except:
        sys.exit("ERROR: Cannot find diag file. Please check segmentation outputs.")
    else:
        return diagFile, maskFile
    
def find_label_params_txt(process):
    '''This function locates label parameters text file for LandTrendr labelling process'''
    
    core1 = "_label_parameters.txt"
    core2 = "_label_parameters_nocover.txt"
    
    #label parameters file named differently for every labelling process type
    if process == "lab_mr227":
        labelTxt = os.path.join(HELPERFILES,"mr227_nbr"+core1)
    elif process == "lab_mr224":
        labelTxt = os.path.join(HELPERFILES,"mr224_nbr"+core1)
    elif process == "lab_nbr":
        labelTxt = os.path.join(HELPERFILES,"nbr"+core2)
    elif process == "lab_mr224_w":
        labelTxt = os.path.join(HELPERFILES,"mr224_wetness"+core1)
    elif process == "lab_mr227_w":
        labelTxt = os.path.join(HELPERFILES,"mr227_wetness"+core1)
    elif process == "lab_band5":
        labelTxt = os.path.join(HELPERFILES,"band5"+core2)
    elif process == "lab_nccn":
        labelTxt = os.path.join(HELPERFILES,"nccn_nbr"+core1)
    else:
        print "ERROR: Process step '{0}' not valid.".format(process)
        
    try:
        os.path.exists(labelTxt)
    except:
        print "ERROR: Label Parameters file does not exist. Expected here: {0}".format(labelTxt) 
        return
    else:  
        return labelTxt  
        
def find_class_code(process):
    '''This function locates class code text file for LandTrendr labelling process'''
    
    #label code filename dependent on the following 3 groups:
    generic = ["lab_mr227", "lab_mr224", "lab_mr227_w", "lab_mr224_w", "lab_band5"]
    nccn = ["lab_nccn"]       
    nbr = ["lab_nbr"]
    if process in generic:
        classTxt = os.path.join(HELPERFILES,"generic_label_codes.txt")
    elif process in nccn:
        classTxt = os.path.join(HELPERFILES,"nccn_label_codes.txt")
    elif process in nbr:
        classTxt = os.path.join(HELPERFILES,"nbr_label_codes_txt")
    else: 
        print "ERROR: Process not valid. Process step choices: {0}".format(generic+nccn+nbr)
     
    try:
        os.path.exists(classTxt)
    except:
        print "ERROR: Label Code file does not exist. Expected here: {0}".format(classTxt) 
        return
    else:  
        return classTxt
    

#---putting it all together....
def convert(sceneNum, sceneDir):
    '''This function finds all necessary parameters for LandTrendr conversion process'''
    projectionPath = PROJECTIONS + "/albers.txt"
    ledapsName = "P" + sceneNum[:3] + "-R" + sceneNum[3:] 
    ledapsPath = os.path.join(sceneDir,ledapsName) 
    outputPath = os.path.join(sceneDir,"images")
    tmpPath = os.path.join(outputPath, "tmp") 
    
    convertParams = {'projectionPath': projectionPath, 'ledapsPath': ledapsPath,
        'outputPath': outputPath, 'tmpPath': tmpPath}
    
    return convertParams #dictionary of parameters
    
def convert_sr(sceneNum, sceneDir):
    '''This function finds all necessary parameters for LandTrendr conversion process'''
    projectionPath = PROJECTIONS + "/albers.txt"
    targzPath = os.path.join(sceneDir,"tar_gz_files") 
    outputPath = os.path.join(sceneDir,"images")
    tmpPath = os.path.join(outputPath, "tmp") 
    
    convertParams = {'projectionPath': projectionPath, 'targzPath': targzPath,
        'outputPath': outputPath, 'tmpPath': tmpPath}
    
    return convertParams #dictionary of parameters
   
def cloudmask_fix(sceneNumber, sceneDir, cldmsk_ref_dates, fix_these_dates):
	'''This function finds all necessary parameters for LandTrendr cloudmask fixation process'''
	cloudParams = {'sceneNumber':sceneNumber, 'sceneDir': sceneDir, 
				   'cldmsk_ref_dates': cldmsk_ref_dates, 'fix_these_dates':fix_these_dates}
	return cloudParams #dictionary of parameters
	 
	
   
def seg(sceneNum, sceneDir, process):
    '''This function finds all necessary parameters for LandTrendr segmentation processes'''   
    
    #use area mask for scene
    useAreaFile = os.path.join(USEAREAS, (sceneNum + '_usearea.bsq')) 
    
    #Default segmentation parameters textfiles 
    if process == "seg_eval":
        segParamBase = "nbr_segmentation_parameters.txt"
        #additional parameters for evaluation mode only
        labelTxtBase = "eval_label_params.txt"
        classTxtBase = "eval_class_codes.txt"
        segEvalSwitch = 1
    elif process == "seg":
        segParamBase = "cmonster_nbr_segmentation_parameters.txt"
    elif process == "seg_w":
        segParamBase = "cmonster_wetness_segmentation_parameters.txt"
    elif process == "seg_band5":
        segParamBase = "band5_segmentation_parameters.txt"
    else:
        sys.exit("ERROR: No segmentation parameters text file found for '{0}'".format(process))
    
    #PUT TOGETHER
    commonParams = {'pathRow': sceneNum, 'sceneDir': sceneDir + "/", 'useArea': useAreaFile, 
        'segParamTxt': os.path.join(HELPERFILES, segParamBase),
        'templateHdr': globalParams.templateHdr}
    try: #if seg_eval, add additional parameters & appropriate switches
        labelTxt = os.path.join(HELPERFILES, labelTxtBase)
        classTxt = os.path.join(HELPERFILES, classTxtBase)
        segEvalSwitches = {'segEvalSwitch': 1, 'segSwitch': 0, 'ftvSwitch': 0, 'darkSegSwitch': 0,
            'labelTxt': labelTxt, 'classTxt': classTxt,
            'withEvalInputs': ", $\n  label_parameters_txt:label_parameters_txt, $\n  class_code_txt:class_code_txt"}
        segParams = dict(commonParams.items() + segEvalSwitches.items())
    except: #if full seg, add appropriate switches
        segSwitches = {'segEvalSwitch': 0, 'segSwitch': 1, 'ftvSwitch': 5, 'darkSegSwitch': 1}
        segParams = dict(commonParams.items() + segSwitches.items())

    return segParams #dictionary of parameters

def lab(sceneDir, process):
    '''This function finds all necessary parameters for LandTrendr change label processes'''
    
    diagFile, maskFile  = find_diag_mask_files(sceneDir, process)
    labelTxt = find_label_params_txt(process)
    classTxt = find_class_code(process)
        
    labParams = {'diagFile': diagFile, 'labelTxt': labelTxt, 'classTxt': classTxt, 
        'templateHdr': globalParams.templateHdr}
    
    return labParams #dictionary of parameters
    
def hist(sceneDir, process):
    '''This function finds all necessary parameters for LandTrendr history variables processes.'''

    diagFile, maskFile = find_diag_mask_files(sceneDir,process)
    
    histParams = {'diagFile': diagFile, 'templateHdr': globalParams.templateHdr} #no mask cases
    if maskFile:
        maskParams = {'maskFile': maskFile, 
            'withMaskInputs': ", maskyes = 1, recovery_mask_override=recovery_mask_override"}
        histParams = dict(histParams.items() + maskParams.items())

    return histParams #dictionary of parameters