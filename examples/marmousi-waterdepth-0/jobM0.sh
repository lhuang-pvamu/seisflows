#!/bin/bash
#SBATCH -J M0-single     # job name
#SBATCH -o M0-single.o%j  # output and error file name (%j expands to jobID)
#SBATCH -N 1                    # total number of nodes requested
#SBATCH --exclusive
#SBATCH -p compute                  # queue (partition)
#SBATCH -t 24:00:00             # run time (hh:mm:ss)

source ~/seis_vars.sh

sfclean
date
sfrun
date
