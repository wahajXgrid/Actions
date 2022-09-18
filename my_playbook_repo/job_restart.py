from robusta.api import *

@action
def job_restart(event: JobEvent):
    job_event = event.get_job()
    job_event.delete()
    
