
import os
import sys
import time

from os.path import abspath, basename, join
from seisflows.tools import unix
from seisflows.tools.tools import call, findpath, saveobj
from seisflows.config import ParameterError, custom_import, intro, parpt

from dask_jobqueue import SLURMCluster
from dask.distributed import Client, wait, get_client

from seisflows.tools.tools import loadjson, loadobj
from seisflows.config import load

from seisflows.system.dask_utils import submit_workflow_dask
from seisflows.system.dask_utils import create_task_dask

#def submit_workflow_dask(output_path):
#
#    print("workflow changing directories to " + output_path)
#    unix.cd(output_path)
#    load(output_path)
#
#    workflow = sys.modules['seisflows_workflow']
#    systyem = sys.modules['seisflows_system']
#    print("running workflow.main()")
#
#    workflow.main()
#    return 42
#
#
#def create_task_dask(mypath, myclass, myfunc, taskid):
#    print("task_creation")
#    # reload from last checkpoint
#    load(mypath)
#
#    # load function arguments
#    kwargspath = join(mypath, 'kwargs')
#    kwargs = loadobj(join(kwargspath, myclass+'_'+myfunc + '.p'))
#
#    # call function
#    func = getattr(sys.modules['seisflows_'+myclass], myfunc)
#    func(**kwargs)
#    sys.stdout.flush()
#


PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']



class dask_slurm(custom_import('system', 'base')):
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
        intro(__name__, dask_slurm.__doc__)
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
            setattr(PAR, 'MEMORY', '16 GB')


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
            raise ParameterError(PAR, 'NNODES')

        # number of processors per node
        if 'CORES' not in PAR:
            raise ParameterError(PAR, 'CORES')


    def submit(self, workflow):
        """ Submits workflow
        """
        # create scratch directories
        unix.mkdir(PATH.SCRATCH)
        unix.mkdir(PATH.SYSTEM)

        # create output directories
        unix.mkdir(PATH.OUTPUT)

        workflow.checkpoint()

        self.cluster = SLURMCluster(cores=12, memory = '16GB', queue = 'compute')#, walltime = PAR.WALLTIME)
        #cluster = SLURMCluster(cores=PAR.CORES, memory = PAR.MEMORY, queue = PAR.QUEUE)#, walltime = PAR.WALLTIME)
        #print(PAR.CORES)
        #print(PAR.MEMORY)
        #print(PAR.QUEUE)

        self.cluster.start_workers(PAR.NNODES)
        print(self.cluster)
        
        time.sleep(1)

        #while len(cluster.running_jobs) < PAR.NNODES:
        #    print(cluster)
        #    time.sleep(1)

        self.client = Client(self.cluster)

        print("submitting job")
        print(self.cluster)
        #TODO: Not sure if this works, might need to use the submit script
        main_workflow = self.client.submit(submit_workflow_dask, PATH.OUTPUT, pure=False)

        print(main_workflow.result())


        

    def run(self, classname, method, *args, **kwargs):
        """ Runs task multiple times in embarrassingly parallel fasion
        """
        self.checkpoint(PATH.OUTPUT, classname, method, args, kwargs)
        futures = []
        client = get_client()

        #for each task
        for taskid in range(PAR.NTASK):
            futures.append(client.submit(create_task_dask, PATH.OUTPUT, classname, method, taskid, pure=False))

        wait(futures)


    def run_single(self, classname, method, *args, **kwargs):
        """ Runs task a single time
        """
        self.checkpoint(PATH.OUTPUT, classname, method, args, kwargs)

        client = get_client()

        future = client.submit(create_task_dask, PATH.OUTPUT, classname, method, 0, pure=False)

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


