from copy import copy
from robusta.api import *

@action
def job_restart(event: JobEvent):
    job_event = event.get_job()
    print(job_event)
    deep_copy = deepcopy(job_event)
    job_event.delete()
    print('*******')
    print(deep_copy)
