#!/bin/tcsh
#$ -pe omp 16
#$ -l h_rt=24:00:00
#$ -N conv033033
#$ -V
cd /projectnb/trenders/scenes/033033/scripts
 module load python/2.7.5
 module load gdal/1.10.0
python convert_ledaps_3333.py
wait

