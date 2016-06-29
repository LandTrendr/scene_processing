#!/usr/bin/env python
'''
Title: batchProcess.py
adapted from Jamie's LT_Processing.py script

This is an executable script that places a .sh file in the indicated directory,
then calls the file, submitting multiple scene processing jobs to cluster. 

Inputs: 
(1) Params Text File (.txt)
(2) Outfile Directory

Outputs:
(1) .sh file within outfile directory given as input
(2) submitted qsub jobs

Note: shell batchfile will be named the same as input params text file

Example: batch_scene_process.py /vol/v1/scenes/batches/params.txt /vl/v1/scenes/batches/
Params File:
"Running conversion for MT Scenes
035035 conversion
036036 conversion
037037 conversion"
'''
import os, sys
import subprocess

LT_USEAREA_MASKS = "/vol/v1/scenes/gnn_snapped_cmon_usearea_files"

def usearea_missing(scene):
    uaFolder = LT_USEAREA_MASKS
    ua_bsq = os.path.join(uaFolder, scene+"_usearea.bsq")
    ua_hdr = os.path.join(uaFolder, scene+"_usearea.hdr")
    return not (os.path.exists(ua_bsq) and os.path.exists(ua_hdr))

def readTxt(params):
    '''This function places info from parameters textfile into a dictionary list'''
    textfile = open(params, 'r')
    next(textfile) #skip first line, used for title
    need_usearea_mask = ["fmask_fix", "seg_eval", "seg", "segw", "seg_band5", "lab_mr224", "lab_mr227",  "lab_mr224_w", "lab_mr227_w", 
                         "lab_nbr", "lab_band5", "lab_nccn"]
    
    processingDict = []
    genList = []
    for ind,line in enumerate(textfile):
        #allows '#' to be used as comment symbol
        if line.startswith('#!'):
            break
        elif line.startswith('#'):
            pass
        else:
            line = line.strip()
            nospace = line.replace(' ', '')
            info = nospace.split(',')
            
        if len(info) != 2:
            print "'{0}' not understood. Skipping over...".format(line)
            pass
        else:
            processingDict.append({'scene': info[0], 'process': info[1]})
            if (processingDict[ind]['process'] in need_usearea_mask) and usearea_missing(info[0]):
                genList.append(info[0])
            
    textfile.close()
    return processingDict, genList
    
def writeBashBatch(batchJobName, outfileDir, processDicts, genList):
    '''This function writes (and then runs) a batchfile of generate_useareas.py and/or 
    prep_script.py statements based on list of process/scene dictionaries'''
    
    #create new bash file
    fileName = os.path.join(outfileDir, batchJobName+".sh")
    batchFile = open(fileName , 'w')
    batchFile.write('#!/bin/bash \n')
    #first write usearea mask statements if necessary
    if len(genList) > 0:
        batchFile.write("generate_useareas.py {0} \n".format(' '.join(genList)))
    #next write all prep_script statements - sub_now is ON
    for i in processDicts:
        batchFile.write("prep_script.py {0} {1} 1 \n".format(i['process'], i['scene'])) 
    batchFile.close()
    
    #ask for permission to execute batch bash file
    ans = raw_input("\nBatchfile {0} complete. Run now? (y/n): ".format(fileName))
    if ans.lower() == 'y':
        print "Fire Away!"
        subprocess.call('sh ' + fileName, shell=True)
    else:
        print "Jobs not submitted. Your batchfile is available here: {0}".format(fileName)
        
        
        
#### Extract Command Line Args & Call Functions ####
def main():
    if len(sys.argv) == 3:
        paramsFileName = sys.argv[1]
        outDir= sys.argv[2]
    else:
        args_err = "Incorrect number of arguments. \nbatchProcess.py inputs: (1)params_file (2)out_dir. \n\n Exiting Process."
        sys.exit(args_err)
    
    if ".txt" in paramsFileName:
        fileNameOnly = paramsFileName.split('/')[-1]
        nameOnly = fileNameOnly[:-4] #this defines batch job name (aka the .sh filename)
    else:
        err1 = "\nPlease use text file of parameters as first input."
        err2 = "\nExample: batchProcess.py params.txt /path/to/outfile/ \nExiting."
        sys.exit(err1+err2)
    
    if os.path.exists(outDir):
        processInfo, genInfo = readTxt(paramsFileName)
        writeBashBatch(nameOnly, outDir, processInfo, genInfo)
    else:
        sys.exit("\nOutfile Directory '{0}' does not exist. Exiting.".format(outDir))
    
main()
