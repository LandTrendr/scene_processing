#!/usr/bin/env python
'''
Title: prep_script.py
Author: Tara Larrue (tlarrue@bu.edu)

This is an executable script that places a qsub bash script & python/idl batchfile
into a scene folder, then runs them.
The bash script runs the indicated scene processing step for the indicated scene.

Inputs: 
(1) processing step 
        [choices- 'convert'; 'fmask_fix'; 'seg_eval'; 'cloudmask_fix'; 'seg'; 'seg_w'; 'seg_band5'
        'lab_mr224'; 'lab_mr227'; 'lab_mr224_w'; 'lab_nbr'; 'lab_band5'; 'lab_nccn'
        'hist_nomask'; 'hist_plusmask', 'hist_w'; 'hist_w_nomask; 'hist_band5_nomask']
(2) scene number string [format: PPPRRR]
(3) submit to cluster? [choices: 0/1]

Outputs:
(1) qsub-ready .sh file in scene scripts directory
(2) idl or python batchfile in scene scripts directory (EXCEPT fmask_fix!)
(3) (if indicated) a submitted job to cluster

Example: 
prep_script.py convert 036031 1

Notes:
This runs DEFAULT state of processing scripts. If you wish to change defaults, choose '0' 
for the 3rd input & edit batch file before submitting the job to the cluster.
'''
import os, sys, subprocess
import datetime
import jinja2 as ji
import sceneUtils #module in scene_processing folder
import getParams  #module in scene_processing folder

TS = str(datetime.datetime.now())
STAMP = "Created via {0} on {1}".format(os.path.basename(__file__),TS)
SCENES = os.environ['LT_SCENES'] #folders where scenes are (sepated by ':')
#below is where qsub & batchfile templates are held
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates") 

class proSets:
    '''Processing Step sets used throughout this script'''
    segs = ["seg", "seg_w", "sega", "seg_band5"]     
    labs = ["lab_mr224", "lab_mr227",  "lab_mr224_w", "lab_mr227_w", "lab_nbr", "lab_band5", "lab_nccn"]
    #'hist' is just a placeholder, not a valid processing step for this script
    hists = ["hist", "hist_plusmask", "hist_w", "hist_w_nomask", "hist_band5_nomask", "hist_nomask"]         
    
def fillTemplatesAndSubmit(aProcessJob, subNow):
    '''This function writes batch files & qsub file based off ProcessJob class instance 
    using jinja2 template tools, then submits job if subNow = 1'''
    enviro = ji.Environment(loader = ji.FileSystemLoader(TEMPLATES_DIR)) #set environment for templates
    for ind, i in enumerate(aProcessJob.tempNames):
        template = enviro.get_template(i) #open template
        newContext = template.render(aProcessJob.paramDicts[ind]) #fill in template
        newFile = open(aProcessJob.fileNames[ind], 'w')
        os.chmod(aProcessJob.fileNames[ind], 0755) #change permissions so qsub can be called from this script
        newFile.write(newContext) #write filled-in template context to new files
        newFile.close()
    
    if subNow:
        subprocess.call('qsub ' + aProcessJob.fileNames[0], shell=True)
    else:
        print "Qsub file has been placed here: '{0}'. Job not submitted. \n\n Exiting.".format(aProcessJob.fileNames[0])
                 
class ProcessJob:   
    def __init__(self, scene, sceneDir):
        self.scene = scene
        self.topDir = sceneDir
        self.tempNames = ["qsub.sh"] #list of templates to fill in (usually a qub script & some batchfile)
        self.fileNames = [] #list of new file names for qsub script & batchfile
        self.paramDicts = [] #list of dictionaries representing template fill-ins for each new file

    def customize(self, process):
        '''This function customizes a ProcessJob class instance based on processing step.'''
        
        #useful definitions for every process
        shrtPR = self.scene[1:3] + self.scene[4:6]
        scriptsDir = os.path.join(self.topDir, "scripts")
        errorDir = os.path.join(self.topDir, "error_output_files")
        shellDict = {'stamp': STAMP, 'error_dir': errorDir} #common qsub script parameters

        #conversion process writes "convert_ledaps.py"
        if process == "convert":
            template = "convert_ledaps{0}.py"
            self.tempNames.append(template.format(''))
            batchFileName = os.path.join(scriptsDir, template.format("_"+self.scene)) 
            shellScriptName = os.path.join(scriptsDir, "cl{0}.sh".format(self.scene))
            self.fileNames.extend([shellScriptName, batchFileName])
  
            shellDict_convert = {'slots': "16", 'run_time': "24:00:00", #qub template parameters unique to conversion
                'job_name': "conv{0}".format(shrtPR), 'script': "python " + batchFileName}
            shellDict = dict(shellDict.items() + shellDict_convert.items())
            self.paramDicts.extend([shellDict, getParams.convert(self.scene, self.topDir)]) #list order is important!
            
        #fmask_fix calls 3 executable python scripts: "FFrek.py"; "Fmask_fix.py"; "mask_replace.py"
        #this uses default 25% threshold    
        #this one is different: NO BATCHFILE WRITTEN!
        elif process == "fmask_fix":
            self.fileNames.append(os.path.join(scriptsDir,"ffix{0}.sh".format(self.scene)))
            #qub template parameters unique to fmask
            shellDict_fmask = {'slots': "1", 'run_time': "24:00:00", 'job_name': "ff{0}".format(shrtPR),
                'script': "FFrek.py {0} {1}\nFmask_fix.py {0} {1} -v 25\nmask_replace.py {0} {1}".format(self.scene,self.topDir)}
            shellDict = dict(shellDict.items() + shellDict_fmask.items())   
            self.paramDicts.append(shellDict)
				
		#manual cloud mask fix.   
        elif process == "cloudmask_fix":
			template = "cloudmask_fix{0}.pro"
			self.tempNames[0]=template.format('')
			batchFileName = os.path.join(scriptsDir, template.format("_"+self.scene)) 
			self.fileNames.extend([batchFileName])
			fix_these_dates = raw_input("enter the fix date [1989231, 1985162, 2011101]: ")   #includes the year and the Julian date 
			cldmsk_ref_dates = raw_input("enter the reference date example [1996228, 2005263]: ") #includes the year and the Julian date 
			getParams.cloudmask_fix(self.scene, self.topDir, cldmsk_ref_dates, fix_these_dates)
			self.paramDicts.extend([getParams.cloudmask_fix(self.scene, self.topDir, cldmsk_ref_dates, fix_these_dates)]) 
		
		
        #segmentation processes writes "run_ledaps_landtrendr_process.pro"
        elif (process == "seg_eval") or (process in proSets.segs):
            template = "run_ledaps_landtrendr_processor{0}.pro"
            self.tempNames.append(template.format(''))
            
            batchFileName = os.path.join(scriptsDir, template.format("_"+self.scene+process.replace('seg','')))
            
            if process == "seg_eval":
                shellScriptName = "segeval{0}.sh".format(self.scene)
                jobName = "sevl{0}".format(shrtPR)
                runTime = "24:00:00"
            else:
                ind = proSets.segs.index(process)
                segNum = "%02d" %(ind+1,) #for qsub job naming purposes
                shellScriptName = "seg{0}_{1}.sh".format(segNum,self.scene)
                jobName = "se{0}.{1}".format(segNum,shrtPR)
                runTime = "120:00:00"
            self.fileNames.extend([os.path.join(scriptsDir,shellScriptName), batchFileName])
            #qub template parameters unique to segmentation
            shellDict_seg = {'slots': "1", 'run_time': runTime, 'job_name': jobName, 'script': "idl " + batchFileName[:-4]}
            shellDict = dict(shellDict.items() + shellDict_seg.items())
            self.paramDicts.extend([shellDict, getParams.seg(self.scene, self.topDir, process)]) #list order is important!
        
        #change label processes write "run_lt_labelfilt.pro" 
        elif process in proSets.labs:
            template = "run_lt_labelfilt{0}.pro"
            self.tempNames.append(template.format(''))
            batchFileName = os.path.join(scriptsDir, template.format("_"+self.scene+process.replace('lab','')))
            ind = proSets.labs.index(process)
            labNum = "%02d" %(ind+1,) #for qsub job naming purposes
            shellScriptName = os.path.join(scriptsDir, "lab{0}_{1}.sh".format(labNum, self.scene))
            self.fileNames.extend([shellScriptName, batchFileName])
            
            shellDict_lab = {'slots': "2", 'run_time': "24:00:00", 'job_name': "lab{0}.{1}".format(labNum,shrtPR), 
                'script': "idl " + batchFileName[:-4]} #qub template parameters unique to labelling
            shellDict = dict(shellDict.items() + shellDict_lab.items())
            self.paramDicts.extend([shellDict, getParams.lab(self.topDir, process)]) #list order is important!
        
        #history variables processes write "create_history_variables_batchfile.pro"
        elif process in proSets.hists[1:]:
            template = "create_history_variables_batchfile{0}.pro"
            self.tempNames.append(template.format(''))
            batchFileName = os.path.join(scriptsDir, template.format("_"+self.scene+process.replace('hist','')))
            ind = proSets.hists.index(process)
            histNum = "%02d" %(ind+1,) #for qsub job naming purposes
            shellScriptName = os.path.join(scriptsDir, "hist{0}_{1}.sh".format(histNum, self.scene))
            self.fileNames.extend([shellScriptName, batchFileName])
            
            shellDict_lab = {'slots': "2", 'run_time': "24:00:00", 'job_name': "hist{0}.{1}".format(histNum,shrtPR), 
                'script': "idl " + batchFileName[:-4]} #qub template parameters unique to history vars
            shellDict = dict(shellDict.items() + shellDict_lab.items())
            self.paramDicts.extend([shellDict, getParams.hist(self.topDir, process)]) #list order is important!
        
        #error handling -- inputted processing step not valid        
        else:
            processErr1 = "\nERROR: LT Processing Step '{0}' not recognized.\n".format(process)
            processErr2 = """Available Processing Steps:
            - 'convert'
            - 'fmask_fix'
            - 'seg_eval'
            - segmentation: '{0}'
            - labelling: '{1}'
            - history vars: '{2}'""".format("'; '".join(i for i in proSets.segs),"'; '".join(i for i in proSets.labs),
                                            "'; '".join(i for i in proSets.hists[1:]))
            print processErr1 + processErr2
        
   
def main(args):
    '''Extract command line args, make some error checks & call functions'''
    #check number of arguments
    if len(args) == 4:
        process = args[1].lower()
        scene = args[2]
    else:
        args_err = "Incorrect number of arguments. \nprep_script.py inputs: " + \
        "(1)process (2)path_row (3)sub_bool. \n\n Exiting Process."
        sys.exit(args_err)
    
    #check 3rd input validity
    err3 = "Invalid 3rd argument. Please enter 0 or 1. \n0=Write qsub file only &" + \
    " do NOT submit job to cluster.\n1=Submit job now.\n\n Exiting Process."
    try:
        subNow = int(args[3])
    except ValueError:
        sys.exit(err3)
    else:
        if subNow !=0 and subNow!=1:
            sys.exit(err3)
    
    #check 1st & 2nd inputs validity, then run create ProcessJob instance & run fillTemplatesAndSubmit
    if sceneUtils.validSceneNum(scene):
        topDirs = SCENES.split(':') #directories where scenes are stored
        scenePath= sceneUtils.findDir(scene,topDirs)
        if scenePath:
            dirCheckGood = sceneUtils.validDirSetup(scenePath, scene)   
            if dirCheckGood:
                myJob = ProcessJob(scene, scenePath)
                myJob.customize(process) #1st input is checked here
                if myJob.paramDicts:
                    fillTemplatesAndSubmit(myJob, subNow)
                else:
                    sys.exit("\n\n Exiting Process.")
            else:
                sys.exit("\n\n Exiting Process.")
        else:
            sys.exit("\n\n Exiting Process.")
    else:
        sys.exit("\n\n Exiting Process.")
	    

if __name__ == '__main__':
    args = sys.argv
    main(args)
    
