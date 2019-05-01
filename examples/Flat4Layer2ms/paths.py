CASE = 'Flat4Layer2ms'

SF_TOP = '~teclee/DAC/FWI/SpecFEM/seisflows/'

SF_SCRATCH = '/scratch/teclee/seisdata/SFtests/'

LOCAL = '/ssd1/teclee/'+CASE

WORKDIR = SF_SCRATCH+CASE

# User-supplied data
#DATA = '/home/teclee/scrseis/SFtests/Flat4Layer/Layer4AC_true/traces/obs2ms/'
DATA = ''

MODEL_TRUE = './Layer4AC_true2ms'

MODEL_INIT = './Layer4AC_init2ms'
#MODEL_INIT = './Layer4AC_const2ms'

PRECOND = ''

SPECFEM_DATA = './specfem2d/DATA'

SPECFEM_BIN = '/home/teclee/DAC/FWI/SpecFEM/specfem2d/bin'

