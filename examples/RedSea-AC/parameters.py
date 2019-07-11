TITLE='RedSea-AC'
WORKFLOW='inversion' # inversion, migration, modeling
#SOLVER='elastic2d' 
SOLVER='specfem2d'   # specfem2d, specfem3d
#SYSTEM='serial'    # serial, pbs, slurm
SYSTEM='slurm_sm'    # serial, pbs, slurm
OPTIMIZE='LBFGS'     # base
#OPTIMIZE='NLCG'     # base
#PREPROCESS='legacy'
PREPROCESS='base'    # base
POSTPROCESS='base'   # base
VERBOSE=3

MISFIT='Waveform'
#MATERIALS='phi_beta'
MATERIALS='Acoustic' # 'Elastic'
DENSITY='Constant'   # 'Constant' 'Variable'


# WORKFLOW
BEGIN=1                 # first iteration
END=80                  # last iteration
#NREC=237                # number of receivers
NSRC=119                 # number of sources
#NSRC=1                 # number of sources
SAVEGRADIENT=5          # save gradient how often
SAVETRACES=5


# PREPROCESSING
FORMAT='su'
#READER='su_specfem2d'   # data file format
#CHANNELS='xz'           # data channels
CHANNELS='p'           # data channels
#NORMALIZE='NormalizeTracesL1'             # normalize
NORMALIZE=0             # normalize
BANDPASS=0              # bandpass
FREQLO=0.               # low frequency corner
FREQHI=0.               # high frequency corner
MUTE=['MuteEarlyArrivals','MuteShortOffsets']
MUTE_EARLY_ARRIVALS_CONST = .300 # sec
MUTE_EARLY_ARRIVALS_SLOPE = 1./2000. # reciprocal of mute vel
MUTE_SHORT_OFFSETS_DIST = 20.  # meters
FLIP_SIGN=True


# OPTIMIZATION
STEPMAX=10              # maximum trial steps
STEPTHRESH=0.1          # step length safeguard


# POSTPROCESSING
SMOOTH=5.               # smoothing radius


# SOLVER
NT=3334                 # number of time steps
DT=.0015                # time step
F0=5.0                  # dominant frequency


# SYSTEM
NTASK=NSRC              # number of tasks
NPROC=1                 # processors per task
WALLTIME=1440            # walltime
#SLURMARGS='--ntasks-per-node=8'

