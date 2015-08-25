#!/usr/bin/env python

#Edited by Tara Larrue 8/14/14

import sys, os, glob, re, shutil

def main(scene,scenePath):

    print '\nWorking on {0}'.format(scene)
    imagesdir = os.path.join(scenePath, 'images')
    repairdir = os.path.join(imagesdir, 'repaired_masks')
    oldmaskdir = os.path.join(scenePath, 'preserved_masks')
    if not os.path.exists(oldmaskdir):
         os.mkdir(oldmaskdir)
    
    oldmaskname = 'L[TE][457]{0}_[0-9][0-9][0-9][0-9]_[0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]_cloudmask.bsq'.format(scene)
    oldmaskPath = os.path.join(imagesdir, '[0-9][0-9][0-9][0-9]', oldmaskname)
    oldmaskList = sorted(glob.glob(oldmaskPath))

    for mask in oldmaskList:
        masknameparts = os.path.split(mask)
	maskname = masknameparts[1]
	maskdir = masknameparts[0]
        fixedmaskname = '2fixed_{0}'.format(maskname)
        fixedmaskPath = os.path.join(repairdir, fixedmaskname)
        if os.path.exists(fixedmaskPath):
           
	    #import pdb; pdb.set_trace() 
	    print 'Replacing {0}'.format(maskname)
            oldfiles = glob.glob(mask.replace('.bsq', '.[bh][sd]*'))
            for f in oldfiles:
                print '\tRemoving {0}'.format(os.path.basename(f))
                shutil.move(f, oldmaskdir)
            newfiles = glob.glob(fixedmaskPath.replace('.bsq', '*'))
            for new in newfiles:
                print '\tAdding {0}'.format(os.path.basename(new))
                newbasename = os.path.basename(new)[len('2fixed_'):]
		newname = os.path.join(maskdir, newbasename)
            	shutil.move(new, newname)

    print 'Done!'


if __name__ == '__main__':

    params = sys.argv
    if len(params) > 0:
        scene = params[1]
        scenePath = params[2]
    else:
        print 'Invalid Scene'
        sys.exit()

    assert re.match('[0-9][0-9][0-9][0-9][0-9][0-9]', scene), 'Invalid Scene'

    sys.exit(main(scene,scenePath))
