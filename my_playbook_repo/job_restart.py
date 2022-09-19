from copy import copy
from robusta.api import *

@action
def job_restart(event: JobEvent):
    job_event = event.get_job()
    print(job_event.apiVersion)
    print('*******')
    print('*******')
    print(job_event.spec)
    # deep_copy = deepcopy(job_event)
    # job_event.delete()
    # print('*******')
    # print(deep_copy)
    # deep_copy.create()
    job_spec = RobustaJob(
        metadata= job_event.metadata,
        spec= job_event.spec,
    
    )
    job_event.delete()
    print(job_spec)
    # job_spec.create()
    # print(job_spec)