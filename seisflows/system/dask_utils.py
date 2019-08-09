
import sys

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
    kwargspath = join(mypath, 'kwargs')
    kwargs = loadobj(join(kwargspath, myclass+'_'+myfunc + '.p'))

    # call function
    func = getattr(sys.modules['seisflows_'+myclass], myfunc)
    func(**kwargs)
    sys.stdout.flush()

