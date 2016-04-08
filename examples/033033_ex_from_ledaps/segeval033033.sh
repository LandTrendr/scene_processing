#!/bin/tcsh

#Created via prep_script.py on 2014-09-05 16:18:37.311677

#$ -pe omp 1
#$ -l h_rt=24:00:00
#$ -N sevl3333
#$ -V
#$ -o /projectnb/trenders/scenes/033033/error_output_files
#$ -e /projectnb/trenders/scenes/033033/error_output_files
idl /projectnb/trenders/scenes/033033/scripts/run_ledaps_landtrendr_processor_033033_eval
wait
