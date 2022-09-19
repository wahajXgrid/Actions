from copy import copy
from pdb import Restart
from robusta.api import *


@action
def job_restart(event: JobEvent, params: EventEnricherParams):
    job_event = event.get_job()
    job_spec = RobustaJob(
        metadata=ObjectMeta(
            name=job_event.metadata.name,
            namespace=job_event.metadata.namespace,
            labels=job_event.metadata.labels,
        ),
        spec=JobSpec(
            completions=job_event.spec.completions,
            parallelism=job_event.spec.parallelism,
            backoffLimit=job_event.spec.backoffLimit,
            manualSelector=job_event.spec.manualSelector,
            activeDeadlineSeconds=job_event.spec.activeDeadlineSeconds,
            selector=job_event.spec.selector,
            ttlSecondsAfterFinished=job_event.spec.ttlSecondsAfterFinished,
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
    job_spec.create()

