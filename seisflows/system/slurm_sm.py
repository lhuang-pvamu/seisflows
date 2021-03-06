
import os
import sys

from os.path import abspath, basename, join
from seisflows.tools import unix
from seisflows.tools.tools import call, findpath, saveobj
from seisflows.config import ParameterError, custom_import, intro, parpt

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class slurm_sm(custom_import('system', 'base')):
    """ Run small 2D inversions on SLURM clusters. 
    All resources are allocated at the beginning and all simulations are run
    within a single job. Requires that each individual wavefield simulation
    runs only a single core.
    """

    def check(self):
        """ Checks parameters and paths
        """
        super(slurm_sm, self).check()
        intro(__name__, slurm_sm.__doc__)
        pars = []

        # name of job
        pars += ['TITLE','WALLTIME']
        if 'TITLE' not in PAR:
            setattr(PAR, 'TITLE', basename(abspath('.')))

        # time allocated for workflow in minutes
        if 'WALLTIME' not in PAR:
            setattr(PAR, 'WALLTIME', 30.)

        pars += ['NTASK','NPROC']

        # how to invoke executables
        pars += ['MPIEXEC']
        if 'MPIEXEC' not in PAR:
            setattr(PAR, 'MPIEXEC', '')

        # optional additional SLURM arguments
        pars += ['SLURMARGS','ENVIRONS','VERBOSE']
        if 'SLURMARGS' not in PAR:
            setattr(PAR, 'SLURMARGS', '')

        # optional environment variable list VAR1=val1,VAR2=val2,...
        if 'ENVIRONS' not in PAR:
            setattr(PAR, 'ENVIRONS', '')

        # level of detail in output messages
        if 'VERBOSE' not in PAR:
            setattr(PAR, 'VERBOSE', 1)

        parpt(PAR,pars)

        # where job was submitted
        if 'WORKDIR' not in PATH:
            setattr(PATH, 'WORKDIR', abspath('.'))

        # where output files are written
        if 'OUTPUT' not in PATH:
            setattr(PATH, 'OUTPUT', PATH.WORKDIR+'/'+'output')

        # where temporary files are written
        if 'SCRATCH' not in PATH:
            setattr(PATH, 'SCRATCH', PATH.WORKDIR+'/'+'scratch')

        # where system files are written
        if 'SYSTEM' not in PATH:
            setattr(PATH, 'SYSTEM', PATH.SCRATCH+'/'+'system')

        # optional local scratch path
        if 'LOCAL' not in PATH:
            setattr(PATH, 'LOCAL', None)

        parpt(PATH, ['WORKDIR','OUTPUT','SCRATCH','SYSTEM','LOCAL'])

        # number of tasks
        if 'NTASK' not in PAR:
            raise ParameterError(PAR, 'NTASK')

        # number of cores per task
        if 'NPROC' not in PAR:
            raise ParameterError(PAR, 'NPROC')


    def submit(self, workflow):
        """ Submits workflow
        """
        # create scratch directories
        unix.mkdir(PATH.SCRATCH)
        unix.mkdir(PATH.SYSTEM)

        # create output directories
        unix.mkdir(PATH.OUTPUT)

        workflow.checkpoint()

        # submit workflow
        print('sbatch '
                + '%s ' %  PAR.SLURMARGS
                + '--job-name=%s '%PAR.TITLE
                + '--output=%s '%(PATH.WORKDIR +'/'+ 'output.log')
                + '--cpus-per-task=%d '%PAR.NPROC
                + '--ntasks=%d '%PAR.NTASK
                + '--time=%d '%PAR.WALLTIME
                + '%s ' % join(findpath('seisflows.system'), 'wrappers/submit')
                + '%s ' % PATH.OUTPUT)
        
        call('sbatch '
                + '%s ' %  PAR.SLURMARGS
                + '--job-name=%s '%PAR.TITLE
                + '--output=%s '%(PATH.WORKDIR +'/'+ 'output.log')
                + '--cpus-per-task=%d '%PAR.NPROC
                + '--ntasks=%d '%PAR.NTASK
                + '--time=%d '%PAR.WALLTIME
                + '%s ' % join(findpath('seisflows.system'), 'wrappers/submit')
                + '%s ' % PATH.OUTPUT)


    def run(self, classname, method, *args, **kwargs):
        """ Runs task multiple times in embarrassingly parallel fasion
        """
        self.checkpoint(PATH.OUTPUT, classname, method, args, kwargs)
        print('srun '
                + '--wait=0 '
                + '%s ' % join(findpath('seisflows.system'), 'wrappers/run ')
                + '%s ' % PATH.OUTPUT
                + '%s ' % classname
                + '%s ' % method
                + '%s ' % PAR.ENVIRONS)
        sys.stdout.flush()

        call('srun '
                + '--wait=0 '
                + '%s ' % join(findpath('seisflows.system'), 'wrappers/run ')
                + '%s ' % PATH.OUTPUT
                + '%s ' % classname
                + '%s ' % method
                + '%s ' % PAR.ENVIRONS)


    def run_single(self, classname, method, *args, **kwargs):
        """ Runs task a single time
        """
        self.checkpoint(PATH.OUTPUT, classname, method, args, kwargs)

        call('srun '
                + '--wait=0 '
                + '--ntasks=1 '
                + '--nodes=1 ' 
                + '%s ' % join(findpath('seisflows.system'), 'wrappers/run ')
                + '%s ' % PATH.OUTPUT
                + '%s ' % classname
                + '%s ' % method
                + '%s ' % PAR.ENVIRONS)


    def hostlist(self):
        """ Generates list of allocated cores
        """
        stdout = check_output('scontrol show hostname $SLURM_JOB_NODEFILE')
        return [line.strip() for line in stdout]


    def taskid(self):
        """ Provides a unique identifier for each running task
        """
        gid = os.getenv('SLURM_GTIDS').split(',')
        lid = int(os.getenv('SLURM_LOCALID'))
        return int(gid[lid])


    def mpiexec(self):
        """ Specifies MPI executable used to invoke solver
        """
        return PAR.MPIEXEC


    def save_kwargs(self, classname, method, kwargs):
        kwargspath = join(PATH.OUTPUT, 'kwargs')
        kwargsfile = join(kwargspath, classname+'_'+method+'.p')
        unix.mkdir(kwargspath)
        saveobj(kwargsfile, kwargs)


