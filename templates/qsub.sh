#!/bin/tcsh

#{{stamp}}

#$ -pe omp {{slots}}
#$ -l h_rt={{run_time}}
#$ -N {{job_name}}
#$ -V
#$ -o {{error_dir}}
#$ -e {{error_dir}}
{{script}}
wait

