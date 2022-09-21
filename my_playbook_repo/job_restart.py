from ast import Break
from copy import copy
from pdb import Restart
from robusta.api import *


@action
def job_restart(event: JobEvent, params: EventEnricherParams):
    job = event.get_job().status.failed
    job_event = event.get_job()
    if job is not None:
        pod = get_job_pod(event.get_job().metadata.namespace,
                          event.get_job().metadata.name)
        status_flag = False
        for status in pod.status.containerStatuses :
            if status.state.terminated.reason == 'Error':
                status_flag = True
                break
        if status_flag:
            print("han bhai theek hy")
            container_list = get_container_list(
                job_event.spec.template.spec.containers)

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

                    activeDeadlineSeconds=job_event.spec.activeDeadlineSeconds,

                    ttlSecondsAfterFinished=job_event.spec.ttlSecondsAfterFinished,
                    template=PodTemplateSpec(
                        spec=PodSpec(
                            containers=container_list,
                            restartPolicy=job_event.spec.template.spec.restartPolicy
                        ),
                    ),

                ),
            )
            job_event.delete()
            job_spec.create()
     

    else:
        print("*****************")
        print("Succeed")


def get_job_pod(namespace, job):
    pod_list = PodList.listNamespacedPod(namespace).obj
    for pod in pod_list.items:
        if pod.metadata.name.startswith(job):
            return pod


def get_container_list(containers_spec):
    containers_list = []
    for  container in containers_spec:
        containers_list.append ( Container(
            name=container.name,
            image=container.image,
            args=container.args,
            command=container.command,
            env=container.env,
            envFrom=container.envFrom,
            imagePullPolicy=container.imagePullPolicy,

        ))
    return containers_list
