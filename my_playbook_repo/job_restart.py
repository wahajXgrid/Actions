from copy import copy
from pdb import Restart
from robusta.api import *


@action
def job_restart(event: JobEvent):
    job_event = event.get_job()

    # deep_copy = deepcopy(job_event)
    # job_event.delete()
    # print('*******')
    # print(deep_copy)
    # deep_copy.create()
    job_spec = RobustaJob(
        metadata=ObjectMeta(
            name=job_event.metadata.name,
            namespace=job_event.metadata.namespace,
            labels=job_event.metadata.labels,
        ),
        spec=JobSpec(
            backoffLimit=job_event.spec.backoffLimit,
            template=PodTemplateSpec(
                spec=PodSpec(
                    containers=[Container(
                        name=job_event.spec.template.spec.containers[0].name,
                        image=job_event.spec.template.spec.containers[0].image,
                    ),
                    ],
                restartPolicy= job_event.spec.template.spec.restartPolicy
                ),
            ),

        ),
    )
    job_event.delete()
    print(job_spec)
    print('*******')
    print('*******')
    print('*******')
    job_spec.create()
    print(job_spec)
