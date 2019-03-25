#!/bin/bash
#SBATCH -J M0-gpu-A     # job name
#SBATCH -o M0-gpu-A%j     # output and error file name (%j expands to jobID)
#SBATCH -N 1                    # total number of nodes requested
#SBATCH --exclusive
#SBATCH -p gpu         # queue (partition)
#SBATCH -t 24:00:00     # run time (hh:mm:ss)

source ~/seis_vars.sh
source ~/gpu_vars.sh

sfcl
date
sfrun
date
