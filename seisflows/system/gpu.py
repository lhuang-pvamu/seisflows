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


class gpu(custom_import('system', 'serial')):
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
        super(gpu, self).check()
        intro(__name__, gpu.__doc__)

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
        gpu0_tasks = dict()
        gpu1_tasks = dict()
        queued_tasks = range(PAR.NTASK)

        # implements "work queue" pattern
        while queued_tasks or gpu0_tasks or gpu1_tasks:

            # launch queued tasks
            while len(queued_tasks) > 0 and \
                  len(gpu0_tasks) < PAR.NTASKMAX:
                i = queued_tasks.pop(0)
                p = self._run_task(classname, method, taskid=i, gpuid=0)
                gpu0_tasks[i] = p
                #sleep(0.1)

            while len(queued_tasks) > 0 and \
                  len(gpu1_tasks) < PAR.NTASKMAX:
                i = queued_tasks.pop(0)
                p = self._run_task(classname, method, taskid=i, gpuid=1)
                gpu1_tasks[i] = p
                #sleep(0.1)

            # checks status of running tasks
            for i, p in gpu0_tasks.items():
                if p.poll() != None:
                    gpu0_tasks.pop(i)
            for i, p in gpu1_tasks.items():
                if p.poll() != None:
                    gpu1_tasks.pop(i)

            if gpu0_tasks or gpu1_tasks:
                sleep(.01)

        print ''


    def run_single(self, classname, method, *args, **kwargs):
        """ Runs task a single time
        """
        os.environ['SEISFLOWS_TASKID'] = str(0)
        func = getattr(__import__('seisflows_'+classname), method)
        func(**kwargs)


    ### private methods

    def _run_task(self, classname, method, taskid=0, gpuid=0):
        env = os.environ.copy().items()
        env += [['SEISFLOWS_TASKID', str(taskid)]]
        env += [['CUDA_VISIBLE_DEVICES',str(gpuid)]]
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

