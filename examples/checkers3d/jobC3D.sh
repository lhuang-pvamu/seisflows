#!/bin/bash
#SBATCH -J 3DCheckers     # job name
#SBATCH -o 3DCheckers.o%j  # output and error file name (%j expands to jobID)
#SBATCH -N 1                    # total number of nodes requested
#SBATCH --exclusive
#SBATCH --ntasks-per-node 16    # total number of processors on each node
#SBATCH -p compute                  # queue (partition)
#SBATCH -t 24:00:00             # run time (hh:mm:ss)

source ~/seis_vars.sh

sfrun
