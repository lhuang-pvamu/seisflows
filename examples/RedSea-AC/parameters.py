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
VERBOSE=4

MISFIT='Envelope'  # 'InstantaneousPhase'  # 'Traveltime' 
#MISFIT = 'Waveform'
#MATERIALS='phi_beta'
MATERIALS='Acoustic' # 'Elastic'
DENSITY='Constant'   # 'Constant' 'Variable'


# WORKFLOW
BEGIN=1                 # first iteration
END=200                  # last iteration
#NREC=237                # number of receivers
NSRC=119                 # number of sources
#NSRC=1                 # number of sources
SAVEGRADIENT=1          # save gradient how often
SAVEKERNELS=SAVEGRADIENT
SAVERESIDUALS=SAVEGRADIENT
SAVETRACES=1


# PREPROCESSING
FORMAT='su'
#READER='su_specfem2d'   # data file format
#CHANNELS='xz'           # data channels
CHANNELS='p'           # data channels
#NORMALIZE='NormalizeTracesL2'             # normalize
#BANDPASS=0              # bandpass
#FREQLO=0.               # low frequency corner
#FREQHI=0.               # high frequency corner
#MUTE=['MuteEarlyArrivals']  # ,'MuteShortOffsets','MuteLongOffsets']
MUTE_EARLY_ARRIVALS_CONST = .300 # sec
MUTE_EARLY_ARRIVALS_SLOPE = 1./1400. # reciprocal of mute vel
MUTE_SHORT_OFFSETS_DIST = 20.  # meters
MUTE_LONG_OFFSETS_DIST = 4000.  # meters
FLIP_SIGN=True


# OPTIMIZATION
LINESEARCH='Backtrack'  # 'Bracket'
#STEPLENMAX=5.
#VPMIN=1300
#VPMAX=5500


# POSTPROCESSING
SMOOTH= 20.               # smoothing radius


# SOLVER
NT=5000                 # number of time steps
DT=.001                # time step
F0=5.0                  # dominant frequency


# SYSTEM
NTASK=NSRC              # number of tasks
NPROC=1                 # processors per task
WALLTIME=1440            # walltime

