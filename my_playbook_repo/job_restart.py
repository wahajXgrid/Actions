from robusta.api import *

@action
def job_restart(event: JobEvent):
    job_event = event.get_job()
    job_temp = set(job_event)
    job_temp.delete()
    print(job_event)
    print('*******')
    print(job_temp)

