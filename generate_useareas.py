#!/usr/bin/env python

import os, sys
from osgeo import gdal, ogr

def formatScene(scene):
    return "{0}{1}".format(int(scene[0:3]), scene[3:6].zfill(3))

def createScene(inScenes, sceneNumber, id_field, buffdist = 2000):
    outfile = "temp_poly"
    if os.path.exists(outfile): os.system("rm -r {0}".format(outfile))
    
    driver = ogr.GetDriverByName('ESRI Shapefile')
    # Read polygon and buffer it
    scenes = driver.Open(inScenes)
    scenesLayer = scenes.GetLayer()
    searchCode = "\"{0}\"={1}".format(id_field, sceneNumber)
    abc = scenesLayer.SetAttributeFilter(searchCode)
    if not scenesLayer.GetFeatureCount() == 1:
        print "{0} came up with {1} results".format(searchCode, scenesLayer.GetFeatureCount())
        sys.exit(1)
    scenesFeature = scenesLayer.GetNextFeature()
    scenesGeom = scenesFeature.GetGeometryRef()

    # Write buffered polygon to a temporary shapefile
    outDs = driver.CreateDataSource(outfile)
    defn = scenesLayer.GetLayerDefn()
    outLayer = outDs.CreateLayer(outfile, scenesLayer.GetSpatialRef(), geom_type=ogr.wkbPolygon)
    outFeat = ogr.Feature(feature_def=outLayer.GetLayerDefn())
    outFeat.SetGeometry(scenesFeature.GetGeometryRef())
    outLayer.CreateFeature(outFeat)
    
    # Close out the datasources
    scenes.Destroy()
    outFeat.Destroy()
    outDs.Destroy()
    os.system("chmod 777 {0}".format(outfile))
    return outfile

def createRaster(polygon, raster, folder):
    polygon_file = "{0}/{0}.shp".format(polygon)
    exec_string = "gdal_rasterize -burn 1 -l {0} -of ENVI -tr 30 30 -ot Byte ".format(polygon)
    exec_string += "{0} {1}".format(polygon_file, raster)
    os.system(exec_string)
    return raster.rstrip(".bsq") + ".hdr"

def updateHeader(oldHeader, refCoords):
    newHeader = oldHeader + "new"
    f = open(oldHeader, "rb")
    g = open(newHeader, "w")
    for line in f:
        if "map info" in line:
            oldCoords = (float(line.split(",")[3]), float(line.split(",")[4]))
            newCoords =[refCoords[0] + round((oldCoords[0] - refCoords[0])/30) * 30,
                        refCoords[1] + round((oldCoords[1] - refCoords[1])/30) * 30]
            for i in range(2): line = line.replace(str(repr(oldCoords[i])), str(repr(newCoords[i])))
        g.write(line)
    f.close()
    g.close()
    os.rename(newHeader, oldHeader)
    
def main(scenes): 
    inputFolder = os.environ['LANDSAT_POLYGONS']
    outputFolder = os.environ['LT_USEAREA_MASKS']
    scenesFile = "wrs_buffer.shp"
    buffer_distance = 2 #  km
    scene_field = "WRS_ALB__1"
    referenceCoords = (-1752510, 1381710)
    os.chdir(inputFolder)

    for original_scene in scenes:
        scene = formatScene(original_scene)
        raster = r"{0}/{1}_usearea.bsq".format(outputFolder, original_scene)
        polygon = createScene(scenesFile, scene, scene_field, 200)
        header = createRaster(polygon, raster, inputFolder)
        updateHeader(header, referenceCoords)        
        print "New mask file created for {0} at {1}".format(scene, raster)

if __name__ == '__main__':
    args = map(str, sys.argv[1:])
    main(args)
