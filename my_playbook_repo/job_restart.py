from ast import Break
from cgitb import reset
from copy import copy
from importlib import resources
from pdb import Restart
import resource
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
        # https://docs.robusta.dev/master/developer-guide/actions/findings-api.html
        pod = get_job_pod(event.get_job().metadata.namespace,
                          event.get_job().metadata.name)

        if pod.status.phase == 'Failed':
            status_flag = False
            for status in pod.status.containerStatuses:
                if status.state.terminated.reason == 'OOMKilled':

                    status_flag = True
                    break

            if status_flag:
                print("han bhai theek hy")
                # for multi-containers
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
            print("Pod is running")

    else:
        print("*****************")
        print("Succeed")


def get_job_pod(namespace, job):
    pod_list = PodList.listNamespacedPod(namespace).obj
    for pod in pod_list.items:
        if pod.metadata.name.startswith(job):
            return pod


def increase_limit(x):
    mem = x.limits['memory']
    req = x.requests['memory']
    num = ''
    num2 = ''
    for x in mem:
        if x.isdigit():
            num = num+x
        else:
            break
    for x in req:
        if x.isdigit():
            num2 = num2+x
        else:
            break
    i = int(num) + 1
    print(i)        
    c = num+"Mi"
    d = num2+"Mi"
    a = ResourceRequirements(limits={"memory" : c},requests={"memory": d})
    return a

def get_container_list(containers_spec):
    containers_list = []

    for container in containers_spec:
        #increase_limit(container.resources)
        containers_list.append(Container(
            name=container.name,
            image=container.image,
            args=container.args,
            command=container.command,
            env=container.env,
            envFrom=container.envFrom,
            imagePullPolicy=container.imagePullPolicy,
            #resources=ResourceRequirements(limits={"memory": "11Mi"},requests={"memory":"6Mi"})
            resources = increase_limit(container.resources)
            #resources= container.resources

        ))
    return containers_list
