from unicodedata import name
from robusta.api import *
from typing import List, Optional
from hikaru.model import Job, PodList


CONTROLLER_UID = "controller-uid"
class IncreaseResources(ActionParams):

    """
    :var increase_by: (optional).Users will specify how much they want to increase in each restart.
    :var max_resource: This variable prevent an infinite loop of job's pod crashing and getting more memory.The action won't increase the memory again when the "Max" limit reached.
    """

    increase_by: Optional[float] = 1
    max_resource: float


@action
def job_restart_on_oomkilled(event: JobEvent, params: IncreaseResources):
    
    """
    This action will run when job failed with oomkilled
    """
    function_name = "job_restart_on_oomkilled"
    finding = Finding(
        title=f"Job Restart",
        source=FindingSource.MANUAL,
        aggregation_key=function_name,
        finding_type=FindingType.REPORT,
        failure=False,
    )
    if not event.get_job():
        logging.error(
            f"job restart was called on event without job: {event}")
        return
    job_event = event.get_job()
    
    """
    Retrieves job's pod information
    """
    try:    
        pod = get_job_latest_pod(job_event)
      
    except:
        logging.error(
            f"get_job_pod was called on event without job: {event}")
    container_name = ''
    index = []
    max_res = []
    status_flag = False
    """
    Retrieves pod's container information for an OOMKilled pod
    """
    oom_killed = "OOMKilled"
    for status in pod.status.containerStatuses:
        if status.state.running == None:
            if status.state.terminated.reason == oom_killed:
                container_name = status.name
    for ind,container in enumerate(pod.spec.containers):
        print(container)

            
                # index.append(ind)
                # status_flag = True
                # max_res.append(PodContainer.get_requests(job_event.spec.template.spec.containers[ind]).memory)
        

        
    print(max_res) 
    print(index)
    
    
    # Extracting request['memory'] from the containers and comparing with max_resource
    # max_res, mem = split_num_and_str(
    #     job_event.spec.template.spec.containers[index].resources.requests["memory"]
    # )
    # if status_flag:
    #     for i in index: 
    #         if float(max_res) < params.max_resource:
    #                 job_spec = restart_job(job_event, params.increase_by, params.max_resource, i)

    #                 job_temp = job_spec.spec.template.spec.containers[i].resources.requests[
    #                     "memory"
    #                 ]
    #                 finding.add_enrichment(
    #                     [
    #                         MarkdownBlock(
    #                             f"*Job Restarted With Memory Increment*\n```\n{job_temp}\n```"
    #                         ),
    #                     ]
    #                 )
    #                 event.add_finding(finding)
    #         else:
    #             job_temp = (
    #                 event.get_job()
    #                 .spec.template.spec.containers[i]
    #                 .resources.requests["memory"]
    #             )
    #             finding.title = f" MAX REACHED "

    #             finding.add_enrichment(
    #                 [
    #                     MarkdownBlock(
    #                         f"*You have reached the memory limit*\n```\n{job_temp}\n```"
    #                     ),
    #                 ]
    #             )
    #             event.add_finding(finding)
    # else:
    #     finding.title = f" POD FAILED "
    #     finding.add_enrichment(
    #         [
    #             MarkdownBlock(
    #                 f"*The job's pod was not killed because of OOM*"
    #             ),
    #         ]
    #     )
    #     event.add_finding(finding)

# Function to restart job
def restart_job(job_event, increase_by, max_resource , index):
    container_list = get_container_list(
        job_event.spec.template.spec.containers, increase_by=increase_by  , max_resource = max_resource ,index = index
    )
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
                    restartPolicy=job_event.spec.template.spec.restartPolicy,
                    nodeName=job_event.spec.template.spec.nodeName,
                    activeDeadlineSeconds=job_event.spec.template.spec.activeDeadlineSeconds,
                    nodeSelector=job_event.spec.template.spec.nodeSelector,
                    affinity=job_event.spec.template.spec.affinity,
                    initContainers=job_event.spec.template.spec.initContainers,
                    serviceAccount=job_event.spec.template.spec.serviceAccount,
                    securityContext=job_event.spec.template.spec.securityContext,
                    volumes=job_event.spec.template.spec.volumes,
                ),
            ),
        ),
    )
    job_event.delete()
    job_spec.create()
    return job_spec


# function to get Containers attributes
def get_container_list(containers_spec, increase_by,max_resource,index):
    count = 0
    containers_list = []
    for container in containers_spec:
        containers_list.append(
            Container(
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
                resources=increase_resource(container.resources, increase_by,max_resource,count,index)
                if (container.resources.limits and container.resources.requests)
                else None,
            )

        )
        count = count + 1
    return containers_list


# Function to increase resources
def increase_resource(resources, increase_by,max_resource,count,index):
    if count == index:
        limits = resources.limits["memory"]
        reqests = resources.requests["memory"]

        split_lim, lim_unit = split_num_and_str(limits)
        split_req, req_unit = split_num_and_str(reqests)

        split_req = float(split_req) + float(increase_by)

        if split_req > float(split_lim):
            split_lim = split_req
        if split_req > max_resource:
            split_req = max_resource
        return ResourceRequirements(
            limits={"memory": (str(split_lim) + lim_unit)},
            requests={"memory": (str(split_req) + req_unit)},
        )
    else:
        return resources


# Function to get job's Pod
def get_job_pod(namespace, job):
    pod_list = PodList.listNamespacedPod(namespace).obj
    for pod in pod_list.items:
        if pod.metadata.name.startswith(job):
            return pod


# Function to split number and string from memory[string]
def split_num_and_str(num_str: str):
    num = ""
    index = None
    for ind, char in enumerate(num_str):
        if char.isdigit() or char is ".":
            num = num + char
        else:
            index = ind
            break
    return num, num_str[index:]




def get_job_latest_pod(job: Job) -> Optional[RobustaPod]:
    if not job:
        return None

    job_labels = job.metadata.labels
    job_selector = f"{CONTROLLER_UID}={job_labels[CONTROLLER_UID]}"

    pod_list: List[RobustaPod] = PodList.listNamespacedPod(
        namespace=job.metadata.namespace,
        label_selector=job_selector
    ).obj.items
    pod_list.sort(key=lambda pod: pod.status.startTime, reverse=True)
    

    return pod_list[0] if pod_list else None

def find_most_recent_oom_killed_container(pod: Pod, container_statuses: List[ContainerStatus], only_current_state: bool = False) -> Optional[PodContainer]:
    latest_oom_kill_container = None
    for container_status in container_statuses:
        oom_killed_container = get_oom_killed_container(pod, container_status, only_current_state)
        if not latest_oom_kill_container or get_oom_kill_time(oom_killed_container) > get_oom_kill_time(latest_oom_kill_container):
            latest_oom_kill_container = oom_killed_container
    return latest_oom_kill_container