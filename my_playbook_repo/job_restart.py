

from urllib import request
from robusta.api import *


class IncreaseResources(ActionParams):
   increase_to: int 

@action
def job_restart(event: JobEvent,params: IncreaseResources):
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
  
        status_flag = False
        # for multi-containers
        for status in pod.status.containerStatuses:
            if status.state.terminated.reason == 'OOMKilled':

                status_flag = True
                break

        if status_flag:
            print("han bhai theek hy")
            
            container_list = get_container_list(
                job_event.spec.template.spec.containers , increase_to=params.increase_to)
        #job_event.spec.template.spec.containers[0].livenessProbe
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
            if pod.status.phase == 'Running':
                print("Job is active")
            else:
                return pod
        else:
            print("There is not pod for this job")


def increase_resource(resource,increase_to):
    limit = resource.limits['memory']
    reqest = resource.requests['memory']
    split_lim = ''
    split_req = ''
    for resource in limit:
        if resource.isdigit(): split_lim = split_lim+resource
        else: break

    for resource in reqest:
        if resource.isdigit(): split_req = split_req+resource  
        else: break

    split_lim = int(split_lim) + increase_to
    split_req = int(split_req) + increase_to


    return ResourceRequirements(limits={"memory" : (str(split_lim)+"Mi")},requests={"memory": (str(split_req)+"Mi")})
    

def get_container_list(containers_spec,increase_to):
    containers_list = []

    for container in containers_spec:
        containers_list.append(Container(
            name=container.name,
            image=container.image,
            livenessProbe=container.livenessProbe,
            securityContext=container.securityContext,
            volumeMounts=container.volumeMounts,
            args=container.args,
            command=container.command,
            ports=container.ports,
            lifecycle=container.lifecycle,
            readinessProbe=container.readinessProbe,
            workingDir=container.workingDir,
            env=container.env,
            startupProbe=container.startupProbe,
            envFrom=container.envFrom,
            imagePullPolicy=container.imagePullPolicy,       
            resources = increase_resource(container.resources,increase_to)
     

        ))
    return containers_list
