VERBOSE=3
TITLE="simple-flat"
WORKFLOW='inversion'    # inversion, migration
#WORKFLOW='test_forward'    # inversion, migration
SOLVER='specfem2d'      # specfem2d, specfem3d
#SYSTEM='serial'       # serial, pbs, slurm
#SYSTEM='multicore'       # serial, pbs, slurm
#SYSTEM='slurm_sm'       # serial, pbs, slurm
SYSTEM='pvc_sm'       # serial, pbs, slurm
OPTIMIZE='LBFGS'        # base, newton
#OPTIMIZE='NLCG'        # base, newton
PREPROCESS='base'       # base
POSTPROCESS='base'      # base

MISFIT='Waveform'
#MATERIALS='LegacyAcoustic'
MATERIALS='Acoustic'
#MATERIALS='Elastic'
DENSITY='Constant'


# WORKFLOW
BEGIN=1                 # first iteration
END=200                   # last iteration
NREC=250                # number of receivers
#NREC=132                # number of receivers
#NSRC=25                 # number of sources
NSRC=20                 # number of sources
SAVEGRADIENT=1          # save gradient how often
SAVETRACES=1


# PREPROCESSING
FORMAT='su'             # data file format
READER='su_specfem2d'
#acoustic should be z or p
CHANNELS='p'            # data channels
#try below for elastic
#CHANNELS='y'            # data channels
#CHANNELS='xz'            # data channels
#NORMALIZE='NormalizeTracesL2'             # normalize
NORMALIZE=0             # normalize
BANDPASS=0              # bandpass
FREQLO=0.               # low frequency corner
FREQHI=0.               # high frequency corner
MUTECONST=0.75          # mute constant
MUTESLOPE=1500.         # mute slope
MUTE='MuteShortOffsets' 
MUTE_SHORT_OFFSETS_DIST=100


# POSTPROCESSING
SMOOTH=10.              # smoothing radius
#SCALE=6.0e6             # scaling factor
SCALE=1             # scaling factor


# OPTIMIZATION
#PRECOND=None            # preconditioner type
#STEPMAX=10              # maximum trial steps
STEPCOUNTMAX=10              # maximum trial steps
STEPTHRESH=0.1          # step length safeguard


# SOLVER
NT=5000                 # number of time steps
DT=1.0e-3                 # time step
#NT=48000                 # number of time steps
#DT=0.006                 # time step
F0=5.0                # dominant frequency


# SYSTEM
NTASK=NSRC                # must satisfy 1 <= NTASK <= NSRC
#NTASK=1                # must satisfy 1 <= NTASK <= NSRC
NPROC=1                 # processors per task
#NPROCMAX=12
WALLTIME=1500            # walltime

#MPIEXEC='mpirun'
FLIP_SIGN="yes"
#SLURMARGS='--ntasks-per-core=1'
SLURMARGS='--exclusive'
