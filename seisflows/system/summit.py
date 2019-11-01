import os
import sys
import numpy as np

from os.path import abspath, basename, join
from subprocess import Popen
from time import sleep

from seisflows.tools import unix
from seisflows.tools.tools import call, findpath, nproc, saveobj
from seisflows.config import ParameterError, custom_import, intro, parpt

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class summit(custom_import('system', 'serial')):
    """ An interface through which to submit workflows, run tasks in serial or 
      parallel, and perform other system functions.

      By hiding environment details behind a python interface layer, these 
      classes provide a consistent command set across different computing
      environments.

      For important additional information, please see 
      http://seisflows.readthedocs.org/en/latest/manual/manual.html#system-configuration
    """

    def check(self):
        """ Checks parameters and paths
        """
        super(summit, self).check()
        intro(__name__, summit.__doc__)

        # number of tasks
        if 'NTASK' not in PAR:
            raise ParameterError(PAR, 'NTASK')

        # number of cores per task
        if 'NPROC' not in PAR:
            raise ParameterError(PAR, 'NPROC')

        # number of available cores
        #if 'NPROCMAX' not in PAR:
        #    setattr(PAR, 'NPROCMAX', nproc())

        # maximum number of concurrent tasks
        if 'NTASKMAX' not in PAR:
            setattr(PAR, 'NTASKMAX', PAR.NPROCMAX/PAR.NPROC)

        parpt(PAR, ['NTASK','NPROC','NPROCMAX','NTASKMAX'])

        # assertions
        assert PAR.NPROC <= PAR.NPROCMAX


    def run(self, classname, method, *args, **kwargs):
        """ Runs task multiple times in embarrassingly parallel fasion

          Executes classname.method(*args, **kwargs) NTASK times, each time on
          NPROC cpu cores
        """
        self.checkpoint(PATH.OUTPUT, classname, method, args, kwargs)

        #running_tasks = dict()
        queued_tasks = list(range(PAR.NTASK))
        num_gpus = 4
        gpu_tasks = []
        for gpu_num in range(num_gpus):
            gpu_tasks.append( dict() )

        # implements "work queue" pattern
        while queued_tasks or gpu_tasks[0] or gpu_tasks[1] or gpu_tasks[2] or gpu_tasks[3]:
            # launch queued tasks
            if len(queued_tasks) > 0:
                idle_gpu = -1
                for gpu_num in range(len(gpu_tasks)):
                    if( not gpu_tasks[gpu_num]):
                        i = queued_tasks.pop(0)
                        gpu_tasks[gpu_num] = self._run_task(classname, method, taskid=i, gpuid=gpu_num)
                        break

            # checks status of running tasks
            for gpu_num in range(len(gpu_tasks)):
                #for p in gpu_tasks[gpu_num].items():
                if gpu_tasks[gpu_num]:
                    if gpu_tasks[gpu_num].poll() != None:
                        gpu_tasks[gpu_num] = None

            if gpu_tasks[0] and gpu_tasks[1] and gpu_tasks[2] and gpu_tasks[3]:
                sleep(.1)

        print('')


    def run_single(self, classname, method, *args, **kwargs):
        """ Runs task a single time
        """
        os.environ['SEISFLOWS_TASKID'] = str(0)
        func = getattr(__import__('seisflows_'+classname), method)
        func(**kwargs)


    ### private methods

    def _run_task(self, classname, method, taskid=0, gpuid=0):
        env = os.environ.copy()
        env['SEISFLOWS_TASKID'] = str(taskid)
        env['CUDA_VISIBLE_DEVICES'] = str(gpuid)
        #env = os.environ.copy().items()
        #env += [['SEISFLOWS_TASKID', str(taskid)]]
        #env += [['CUDA_VISIBLE_DEVICES',str(gpuid)]]
        self.progress(taskid)

        p = Popen(
            findpath('seisflows.system') +'/'+ 'wrappers/run '
            + PATH.OUTPUT + ' '
            + classname + ' '
            + method,
            shell=True,
            env=dict(env))

        return p

    def mpiexec(self):
        cuda_var = os.getenv('CUDA_VISIBLE_DEVICES')
        if cuda_var:
            num_str = cuda_var
        else:
            num_str="0,1"
            seis_env = os.getenv('SEISFLOWS_TASKID')
            if seis_env:
                taskid = int(seis_env)
                gpu_num = taskid%2
                num_str = str(gpu_num)
        return "CUDA_VISIBLE_DEVICES=" + num_str

    def save_kwargs(self, classname, method, kwargs):
        kwargspath = join(PATH.OUTPUT, 'kwargs')
        kwargsfile = join(kwargspath, classname+'_'+method+'.p')
        unix.mkdir(kwargspath)
        saveobj(kwargsfile, kwargs)

