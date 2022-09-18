from robusta.api import *

@action
def job_restart(event: JobEvent):
    job_event = event.get_job()
    print(job_event)
    job_event.delete()
    print('*******')
    print(job_event)
