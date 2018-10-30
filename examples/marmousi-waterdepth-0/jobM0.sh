#!/bin/bash
#SBATCH -J M0-MT     # job name
#SBATCH -o M0-MT.o%j  # output and error file name (%j expands to jobID)
#SBATCH -N 1                    # total number of nodes requested
#SBATCH --exclusive
#SBATCH --ntasks-per-node 16    # total number of processors on each node
#SBATCH -p compute                  # queue (partition)
#SBATCH -t 24:00:00             # run time (hh:mm:ss)

source ~/seis_vars.sh

sfclean
sfrun
