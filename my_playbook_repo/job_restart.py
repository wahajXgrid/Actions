from ast import Break
from cgitb import reset
from copy import copy
from pdb import Restart
from robusta.api import *


@action
def job_restart(event: JobEvent):
    function_name = "job_restart"
    finding = Finding(
        title=f"JOB RESTART",
        source=FindingSource.MANUAL,
        aggregation_key=function_name,
        finding_type=FindingType.REPORT,
        failure=False,
    )
    job_temp = event.get_job()

    finding.add_enrichment(
        [
            MarkdownBlock(
                f"*job*restart*\n```\n{job_temp}\n```"
            ),
        ]
    )
    event.add_finding(finding)
    job = event.get_job().status.failed
    job_event = event.get_job()
    if job is not None:
      
    #   txt = job_event.spec.template.spec.containers[0].resources.limits['memory']
    
    #   num=''
    #   for x in txt:
    #     if x.isdigit():
    #         num=num+x
    #     else:
    #         break
    #   print(int(num))

        # https://docs.robusta.dev/master/developer-guide/actions/findings-api.html
        pod = get_job_pod(event.get_job().metadata.namespace,
                          event.get_job().metadata.name)
        status_flag = False
        for status in pod.status.containerStatuses:
            if status.state.terminated.reason == 'OOMKilled':
                status_flag = True
                break

        if status_flag:
            print("han bhai theek hy")
            #for multi-containers
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
    for container in containers_spec:
        containers_list.append(Container(
            name=container.name,
            image=container.image,
            args=container.args,
            command=container.command,
            env=container.env,
            envFrom=container.envFrom,
            imagePullPolicy=container.imagePullPolicy,
            resources=container.resources
        ))
    return containers_list
