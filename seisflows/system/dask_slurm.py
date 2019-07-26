
import os
import sys

from os.path import abspath, basename, join
from seisflows.tools import unix
from seisflows.tools.tools import call, findpath, saveobj
from seisflows.config import ParameterError, custom_import, intro, parpt

from dask_jobqueue import SLURMCluster
from dask.distributed import Client
from dask.distributed import wait

from seisflows.tools.tools import loadjson, loadobj
from seisflows.config import load

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']

def create_task_dask(mypath, myclass, myfunc, taskid):
    print("task_creation")
    # reload from last checkpoint
    load(mypath)

    # load function arguments
    kwargspath = join(mypath, 'kwargs')
    kwargs = loadobj(join(kwargspath, myclass+'_'+myfunc + '.p'))

    # call function
    func = getattr(sys.modules['seisflows_'+myclass], myfunc)
    func(**kwargs)
    sys.stdout.flush()



class dask_sm(custom_import('system', 'base')):
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

        if 'QUEUE' not in  PAR:
            setattr(PAR, 'QUEUE', 'compute')

        if 'MEMORY' not in  PAR:
            setattr(PAR, 'MEMORY', '50 GB')


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
        
        # number of nodes to run on
        if 'NNODES' not in PAR:
            raise ParameterError(PAR, 'NPROC')

        # number of processors per node
        if 'CORES' not in PAR:
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

        cluster = SLURMCluster(cores=PAR.CORES, memory = PAR.MEMORY, queue = PAR.QUEUE, walltime = PAR.WALLTIME)
        cluster.scale(PAR.NNODES)
        client = Client(cluster)

        #TODO: Not sure if this works, might need to use the submit script
        client.submit(workflow.main)

        

    def run(self, classname, method, *args, **kwargs):
        """ Runs task multiple times in embarrassingly parallel fasion
        """
        self.checkpoint(PATH.OUTPUT, classname, method, args, kwargs)
        futures = []

        #for each task
        for taskid in PAR.NTASK:
            futures.append(client.submit(create_task_dask, PATH.OUTPUT, classname, method, taskid, pure=False))

        wait(futures)


    def run_single(self, classname, method, *args, **kwargs):
        """ Runs task a single time
        """
        self.checkpoint(PATH.OUTPUT, classname, method, args, kwargs)

        future = client.submit(run, PATH.OUTPUT, classname, method, 0, pure=False))

        wait(future)


    def taskid(self):
        """ Provides a unique identifier for each running task
        """
        #TODO: how do I store this in task creation and access it here?

        #gid = os.getenv('SLURM_GTIDS').split(',')
        #lid = int(os.getenv('SLURM_LOCALID'))
        #return int(gid[lid])


    def mpiexec(self):
        """ Specifies MPI executable used to invoke solver
        """
        return PAR.MPIEXEC


#    def save_kwargs(self, classname, method, kwargs):
#       kwargspath = join(PATH.OUTPUT, 'kwargs')
#       kwargsfile = join(kwargspath, classname+'_'+method+'.p')
#       unix.mkdir(kwargspath)
#       saveobj(kwargsfile, kwargs)


