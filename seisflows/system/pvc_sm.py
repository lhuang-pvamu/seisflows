
import os
import sys
import time

from os.path import abspath, basename, join
from seisflows.tools import unix
from seisflows.tools.tools import call, findpath, saveobj
from seisflows.config import ParameterError, custom_import, intro, parpt

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class pvc_sm(custom_import('system', 'base')):
    """ An interface through which to submit workflows, run tasks in serial or 
      parallel, and perform other system functions.

      By hiding environment details behind a python interface layer, these 
      classes provide a consistent command set across different computing
      environments.

      Intermediate files are written to a global scratch path PATH.SCRATCH,
      which must be accessible to all compute nodes.

      Optionally, users can provide a local scratch path PATH.LOCAL if each
      compute node has its own local filesystem.

      For important additional information, please see 
      http://seisflows.readthedocs.org/en/latest/manual/manual.html#system-configuration
    """


    def check(self):
        """ Checks parameters and paths
        """
        intro(__name__, pvc_sm.__doc__)
        pars = []
        paths = []

        # name of job
        pars += ['TITLE']
        if 'TITLE' not in PAR:
            setattr(PAR, 'TITLE', basename(abspath('.')))

        # time allocated for workflow in minutes
        pars += ['WALLTIME']
        if 'WALLTIME' not in PAR:
            setattr(PAR, 'WALLTIME', 30.)

        # number of tasks
        pars += ['NTASK','NPROC']

        # number of tasks per node
        pars += ['NODESIZE']
        if 'NODESIZE' not in PAR:
            setattr(PAR, 'NODESIZE', 12)

        # how to invoke executables
        pars += ['MPIEXEC']
        if 'MPIEXEC' not in PAR:
            setattr(PAR, 'MPIEXEC', '')

        # optional additional PBS arguments
        pars += ['SLURMARGS','ENVIRONS','VERBOSE']
        if 'SLURMARGS' not in PAR:
            setattr(PAR, 'SLURMARGS', '')

        # optional environment variable list VAR1=val1,VAR2=val2,...
        if 'ENVIRONS' not in PAR:
            setattr(PAR, 'ENVIRONS', '')

        # level of detail in output messages
        if 'VERBOSE' not in PAR:
            setattr(PAR, 'VERBOSE', 1)

        # where job was submitted
        paths += ['WORKDIR']
        if 'WORKDIR' not in PATH:
            setattr(PATH, 'WORKDIR', abspath('.'))

        # where output files are written
        paths += ['OUTPUT']
        if 'OUTPUT' not in PATH:
            setattr(PATH, 'OUTPUT', PATH.WORKDIR+'/'+'output')

        # where temporary files are written
        paths += ['SCRATCH']
        if 'SCRATCH' not in PATH:
            setattr(PATH, 'SCRATCH', PATH.WORKDIR+'/'+'scratch')

        # where system files are written
        paths += ['SYSTEM']
        if 'SYSTEM' not in PATH:
            setattr(PATH, 'SYSTEM', PATH.SCRATCH+'/'+'system')

        # optional local filesystem scratch path
        paths += ['LOCAL']
        if 'LOCAL' not in PATH:
            setattr(PATH, 'LOCAL', None)

        # report
        parpt(PAR, pars)
        parpt(PATH, paths)        

        # number of tasks
        if 'NTASK' not in PAR:
            raise ParameterError(PAR, 'NTASK')

        # number of cores per task
        if 'NPROC' not in PAR:
            raise ParameterError(PAR, 'NPROC')

        # number of cores per node
        if 'NODESIZE' not in PAR:
            raise ParameterError(PAR, 'NODESIZE')


    def submit(self, workflow):
        """ Submits workflow
        """
        # create scratch directories
        unix.mkdir(PATH.SCRATCH)
        unix.mkdir(PATH.SYSTEM)

        # create output directories
        unix.mkdir(PATH.OUTPUT)

        workflow.checkpoint()

        TASKS_PER_NODE = PAR.NODESIZE / PAR.NPROC
        #OMP_NT = os.getenv('OMP_NUM_THREADS')
        os.environ['OMP_NUM_THREADS'] = str(PAR.NPROC)

        # submit workflow
        print('sbatch '
                + '%s ' %  PAR.SLURMARGS
                + '--exclusive ' 
                + '--job-name=%s '%PAR.TITLE
                + '--output=%s '%(PATH.WORKDIR +'/'+ 'output.log')
                + '--cpus-per-task=%d '%PAR.NPROC
                + '--ntasks-per-node=%d '%TASKS_PER_NODE
                + '--ntasks=%d '%PAR.NTASK
                + '--time=%d '%PAR.WALLTIME
                + '%s ' % join(findpath('seisflows.system'), 'wrappers/submit')
                + '%s ' % PATH.OUTPUT)
        
        call('sbatch '
                + '%s ' %  PAR.SLURMARGS
                + '--exclusive ' 
                + '--job-name=%s '%PAR.TITLE
                + '--output=%s '%(PATH.WORKDIR +'/'+ 'output.log')
                + '--cpus-per-task=%d '%PAR.NPROC
                + '--ntasks-per-node=%d '%TASKS_PER_NODE
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

        t1 = time.time()
        call('srun '
                + '--wait=0 '
                + '%s ' % join(findpath('seisflows.system'), 'wrappers/run ')
                + '%s ' % PATH.OUTPUT
                + '%s ' % classname
                + '%s ' % method
                + '%s ' % PAR.ENVIRONS)
        print classname + "." + method + ":  " + str(time.time()-t1)

    def run_single(self, classname, method, *args, **kwargs):
        """ Runs task a single time
        """
        self.checkpoint(PATH.OUTPUT, classname, method, args, kwargs)


        t1 = time.time()
        call('srun '
                + '--wait=0 '
                + '--ntasks=1 '
                + '--nodes=1 ' 
                + '%s ' % join(findpath('seisflows.system'), 'wrappers/run ')
                + '%s ' % PATH.OUTPUT
                + '%s ' % classname
                + '%s ' % method
                + '%s ' % PAR.ENVIRONS)
        print classname + "." + method + ":  " + str(time.time()-t1)


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


