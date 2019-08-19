
import sys
import os

from seisflows.tools import unix
from seisflows.tools.tools import loadjson, loadobj
from seisflows.config import load


def submit_workflow_dask(output_path):

    print("workflow changing directories to " + output_path)
    unix.cd(output_path)
    load(output_path)

    workflow = sys.modules['seisflows_workflow']
    systyem = sys.modules['seisflows_system']
    print("running workflow.main()")

    workflow.main()
    return 42


def create_task_dask(mypath, myclass, myfunc, taskid):
    print("task_creation")
    # reload from last checkpoint
    load(mypath)

    # load function arguments
    kwargspath = os.path.join(mypath, 'kwargs')
    kwargs = loadobj(os.path.join(kwargspath, myclass+'_'+myfunc + '.p'))

    # call function
    func = getattr(sys.modules['seisflows_'+str(myclass)], myfunc)
    print("calling task function")
    func(**kwargs)
    sys.stdout.flush()

