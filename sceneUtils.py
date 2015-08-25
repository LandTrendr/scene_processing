'''
Title: sceneUtils.py
Author: Tara Larrue (tlarrue@bu.edu)

This python module contains general scene processing utilities.
'''
import os, subprocess

def findDir(scene,topDirs):
    '''This function looks through list of top directories to return correct directory of inputted scene'''
    
    #find all locations where input scene is located
    trueDirs = [] #list of input scene locations
    for i in topDirs: 
        sceneDir = os.path.join(i,scene)
        if os.path.exists(sceneDir):
            trueDirs.append(sceneDir)
    
    #if scene is found in more than one of those locations, ask user to choose.   
    if len(trueDirs) > 1:
        print "\nFound directories in multiple places for scene {0}, please choose desired directory: ".format(scene)
        for j in trueDirs:
            print "\n[{0}]: {1}".format(str(trueDirs.index(j)+1), j)
        attempt = 1
        good_input = False            
        answer = raw_input('\nChoose Number (ie. 1 or 2): ')
        while good_input==False:
            try:
                ind = int(answer)
                selectDir = trueDirs[ind-1]
            except:
                if attempt < 3:
                    answer = raw_input("Input not understood. Please choose valid number: ")
                    attempt += 1
                else:
                    print "\nERROR: Input not understood. 3 attempt limit reached."
                    return None
            else:
                good_input = True
        return selectDir      
    #if scene in only one location, choose that location.
    elif len(trueDirs) == 1:
        return trueDirs[0]
    #if scene not found, return error.
    else:
        print "\nERROR: Scene Directory Not Found For {0}".format(scene)
        return None
        
def validSceneNum(scene):
    '''This function checks scene number input for validity'''
    cond1 = (len(scene) == 6)
    try: 
        val = int(scene)
    except ValueError:
        cond2 = False
    else:
        cond2 = True
    if cond1 and cond2:
        return True
    else:
        print "\nERROR: Scene Input is not a valid 6-digit scene number (format: PPPRRR)."
        return False    
        
def dirCleanLedaps(scene_dir, scene):
    '''This function moves LEDAPS job output files'''
    ledapsJob = "l" + scene[1:3] + scene[4:6]
    itemsInDir = os.listdir(scene_dir)
    
    for i in itemsInDir:
        if i.startswith(ledapsJob):
            needClean = True
            break
    else:
        needClean = False
        
    if needClean:
        print "Cleaning up LEDAPS outputs..."
        subprocess.call("mv {0}* {1}".format(os.path.join(scene_dir,ledapsJob),os.path.join(scene_dir,"error_output_files")), shell=True)
           
def validDirSetup(scene_dir, scene):
    '''This function defines scene directory requirements & checks for errors in directory set-up'''
    #define all conditions
    ledaps = "P" + scene[:3] + "-R" + scene[3:]
    dir_requires = [ledaps, "images", "images/tmp", "error_output_files", "scripts"]
    
    dirCleanLedaps(scene_dir, scene)
    
    #check for missing requirements
    dirs_needed = []
    for i in dir_requires:
        req_dir = os.path.join(scene_dir,i)
        if not os.path.exists(req_dir):
            dirs_needed.append(req_dir)
            
    #if a directory is missing, make it unless it is ledaps
    if len(dirs_needed) > 0:
        print "\nMissing directory set-up requirements...\n"
        if os.path.join(scene_dir,ledaps) in dirs_needed:
            print "LEDAPS outputs are missing. Cannot create this folder: {0}. Please run LEDAPS script first.".format(ledaps)
            return False
        else:
            for j in dirs_needed:
                print "New Directory Made: {0} ".format(j)
                subprocess.call("mkdir {0}".format(j),shell=True)
            return True         
    else:
        return True   
        
    
        
        
            
    
    
    