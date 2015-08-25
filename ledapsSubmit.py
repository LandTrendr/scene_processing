#!/usr/bin/env python
'''
Example: 
ledapsSubmit.py 036031
'''
#modified 8/21/14 for scene_processing module

#LEDAPS Uploader v1.7b by Jamie Perkins
#Use this program to generate and execute the proper command line script for submitting jobs to LEDAPS
#Contact: jperkins@bu.edu

import os, sys
import subprocess
import sceneUtils as su

def main(args):
    '''Extract command line args, find scene directory & construct ledaps command line'''
    if len(args) == 2:
        scene = args[1]    
        topDirs = os.environ['LT_SCENES'].split(':') #directories where scenes are stored
        scenePath = su.findDir(scene,topDirs)
    else:
        sys.exit("Incorrect number of arguments. Input: [1]path_row \n\n Exiting Process.")
    
    #check that there are tar.gz files in scene folder
    for file in os.listdir(scenePath):
        if file.endswith(".tar.gz"):
            break
    else:
        sys.exit("\nNo tar.gz files found in {0}.\nPlease verify images were downloaded correctly.\n\n Exiting Process.".format(scenePath))
    
    #compile terminal command & display        
    jobId = "l" + scene[1:3] + scene[4:6]
    cmdout = "sh landsatPrepSubmit.sh -m 8 -n {0} -w 60 -p 12.5 -d -c 5 -s 4 {1}".format(jobId,scenePath) 

    print "\n\nYour command line code:"
    print "\n-------------------------------------------------------------------------"
    print cmdout 
    print "-------------------------------------------------------------------------"
    
    #ask user if they want to submit ledaps job
    cmdline = raw_input("Run Ledaps (y/n)?: ")

    while cmdline.lower() != "y" and cmdline.lower() != "n":        
        print "Sorry, input not understood. Please enter 'y' or 'n'.\n\n"
        cmdline = raw_input("Run Ledaps (y/n)?: ")
    
    #make error_output_files dir before running ledaps script
    if cmdline.lower() == "y":    
        errOutDir = os.path.join(scenePath,"error_output_files") #
        if not os.path.exists(errOutDir):
            print "\nNew Directory Made: {0}".format(errOutDir)
            subprocess.call("mkdir {0}".format(errOutDir), shell=True)  
        print "\n\nStarting LEDAPS script. Do NOT close this terminal!\n\n"   
        subprocess.call(cmdout, shell=True)
        
    else:
        print "\nLEDAPS has not run. \n\n Exiting."


if __name__ == '__main__':
    args = sys.argv
    main(args)