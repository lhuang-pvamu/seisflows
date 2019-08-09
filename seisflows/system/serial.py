
import os
import sys
import numpy as np

from os.path import abspath, basename, join
from seisflows.tools import unix
from seisflows.config import ParameterError, custom_import, intro, parpt

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class serial(custom_import('system', 'base')):
    "Implements workflow serially instead of in parallel, for testing. "

    def check(self):
        """ Checks parameters and paths
        """
        super(serial, self).check()

        intro(__name__, serial.__doc__)
        pars = []
        paths = []

        # name of job
        pars += ['TITLE']
        if 'TITLE' not in PAR:
            setattr(PAR, 'TITLE', basename(abspath('.')))

        # number of tasks
        pars += ['NTASK']
        if 'NTASK' not in PAR:
            setattr(PAR, 'NTASK', 1)

        # number of processers per task
        pars += ['NPROC']
        if 'NPROC' not in PAR:
            setattr(PAR, 'NPROC', 1)

        # how to invoke executables
        pars += ['MPIEXEC']
        if 'MPIEXEC' not in PAR:
            setattr(PAR, 'MPIEXEC', '')

        # level of detail in output messages
        pars += ['VERBOSE']
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

    def submit(self, workflow):
        """ Submits job
        """
        # create scratch directories
        unix.mkdir(PATH.SCRATCH)
        unix.mkdir(PATH.SYSTEM)

        # create output directories
        unix.mkdir(PATH.OUTPUT)

        workflow.checkpoint()

        # execute workflow
        workflow.main()


    def run(self, classname, method, hosts='all', **kwargs):
        """ Executes task multiple times in serial
        """
        unix.mkdir(PATH.SYSTEM)

        for taskid in range(PAR.NTASK):
            os.environ['SEISFLOWS_TASKID'] = str(taskid)
            if PAR.VERBOSE > 0:
                self.progress(taskid)
            func = getattr(__import__('seisflows_'+classname), method)
            func(**kwargs)
        print( '' )


    def run_single(self, classname, method, *args, **kwargs):
        """ Runs task a single time
        """
        os.environ['SEISFLOWS_TASKID'] = str(0)
        func = getattr(__import__('seisflows_'+classname), method)
        func(**kwargs)


    def taskid(self):
        """ Provides a unique identifier for each running task
        """
        return int(os.environ['SEISFLOWS_TASKID'])


    def mpiexec(self):
        """ Specifies MPI executable used to invoke solver
        """
        return PAR.MPIEXEC


    def progress(self, taskid):
        """ Provides status update
        """
        if PAR.NTASK > 1:
            print( ' task ' + '%02d of %02d' % (taskid+1, PAR.NTASK) )
