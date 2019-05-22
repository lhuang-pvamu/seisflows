TITLE='Flat4LayerAC_2ms'
WORKFLOW='inversion' # inversion, migration, modeling
#SOLVER='elastic2d' 
SOLVER='specfem2d'   # specfem2d, specfem3d
#SYSTEM='serial'    # serial, pbs, slurm
SYSTEM='slurm_sm'    # serial, pbs, slurm
OPTIMIZE='LBFGS'     # base
#OPTIMIZE='NLCG'     # base
PREPROCESS='base'    # base
POSTPROCESS='base'   # base
VERBOSE=2

MISFIT='Waveform'
#MATERIALS='phi_beta'
MATERIALS='Acoustic'  # 'Elastic'
DENSITY='Constant'


# WORKFLOW
BEGIN=40                # first iteration
END=100                 # last iteration
NREC=399                # number of receivers
NSRC=99                 # number of sources
#NSRC=1                 # number of sources
SAVEGRADIENT=1          # save gradient how often


# PREPROCESSING
FORMAT='su'
READER='su_specfem2d'   # data file format
CHANNELS='p'           # data channels- p pressure, xz displacement
#NORMALIZE=1             # normalize
NORMALIZE=0             # normalize
BANDPASS=0              # bandpass
FREQLO=0.               # low frequency corner
FREQHI=0.               # high frequency corner

MUTE=['MuteEarlyArrivals','MuteShortOffsets']
MUTE_EARLY_ARRIVALS_CONST = .300 # sec
MUTE_EARLY_ARRIVALS_SLOPE = 1./1500. # reciprocal of water vel
MUTE_SHORT_OFFSETS_DIST = 50.  # meters


# OPTIMIZATION
STEPCOUNTMAX=10              # maximum trial steps
STEPTHRESH=0.1          # step length safeguard
FLIP_SIGN='yes'


# POSTPROCESSING
SMOOTH=5.               # smoothing radius
SCALE=1.                # scaling factor


# SOLVER
NT=3000                 # number of time steps
DT=2.e-3                # time step
F0=5.                  # dominant frequency
SAVETRACES = 1


# SYSTEM
NTASK=NSRC              # number of tasks
NPROC=1                 # processors per task
WALLTIME=1500            # walltime

SLURMARGS='--ntasks-per-node=9'

