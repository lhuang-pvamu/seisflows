VERBOSE=3
TITLE="checkers"
WORKFLOW='inversion'    # inversion, migration
SOLVER='specfem2d'      # specfem2d, specfem3d
#SYSTEM='serial'       # serial, pbs, slurm
#SYSTEM='multicore'       # serial, pbs, slurm
SYSTEM='slurm_sm'       # serial, pbs, slurm
OPTIMIZE='LBFGS'        # base, newton
PREPROCESS='base'       # base
POSTPROCESS='base'      # base

MISFIT='Waveform'
MATERIALS='LegacyAcoustic'
#MATERIALS='Elastic'
DENSITY='Constant'


# WORKFLOW
BEGIN=1                 # first iteration
END=10                   # last iteration
NREC=132                # number of receivers
NSRC=25                 # number of sources
#NSRC=12                 # number of sources
SAVEGRADIENT=1          # save gradient how often


# PREPROCESSING
FORMAT='su'             # data file format
READER='su_specfem2d'
#acoustic should be z or p
#CHANNELS='p'            # data channels
#try below for elastic
#CHANNELS='y'            # data channels
CHANNELS='xz'            # data channels
NORMALIZE=0             # normalize
BANDPASS=0              # bandpass
FREQLO=0.               # low frequency corner
FREQHI=0.               # high frequency corner


# POSTPROCESSING
SMOOTH=20.              # smoothing radius
SCALE=6.0e6             # scaling factor


# OPTIMIZATION
#PRECOND=None            # preconditioner type
#STEPMAX=10              # maximum trial steps
STEPCOUNTMAX=10              # maximum trial steps
STEPTHRESH=0.1          # step length safeguard


# SOLVER
NT=48000                 # number of time steps
DT=0.006                 # time step
#DT=0.06                 # time step
F0=0.084                # dominant frequency


# SYSTEM
NTASK=NSRC                # must satisfy 1 <= NTASK <= NSRC
#NTASK=1                # must satisfy 1 <= NTASK <= NSRC
#NPROC=1                 # processors per task
NPROC=2                 # processors per task
#NPROCMAX=12
WALLTIME=500            # walltime

#MPIEXEC='mpirun'
#SLURMARGS='--ntasks-per-core=1'
