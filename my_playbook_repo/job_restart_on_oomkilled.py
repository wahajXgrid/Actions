from robusta.api import *
from bitmath import *
CONTROLLER_UID = "controller-uid"


class IncreaseResources(ActionParams):

    """
    :var increase_by: (optional).Users will specify how much they want to increase in each restart.
    :var max_resource: This variable prevent an infinite loop of job's pod crashing and getting more memory.The action won't increase the memory again when the "Max" limit reached.
    """

    increase_by: Optional[str] = 1
    max_resource: float


@action
def job_restart_on_oomkilled(event: JobEvent, params: IncreaseResources):
    """
    This action will run when job failed with oomkilled
    """
    function_name = "job_restart_on_oomkilled"
    finding = Finding(
        title=f"JOB RESTART",
        source=FindingSource.MANUAL,
        aggregation_key=function_name,
        finding_type=FindingType.REPORT,
        failure=False,
    )
    if not event.get_job():
        logging.error(f"job restart was called on event without job: {event}")
        return
    job_event = event.get_job()

    """
    Retrieves job's pod information
    """
    try:
        pod = get_job_latest_pod(job_event)

    except:
        logging.error(f"get_job_pod was called on event without job: {event}")
        return

    containers = []
    oomkilled_containers = []
    running_containers = []

    """
    Retrieves pod's containers information
    """
    OOMKilled = "OOMKilled"
    for status in pod.status.containerStatuses:
        if status.state.running == None:
            if status.state.terminated.reason == OOMKilled:
                oomkilled_containers.append(status.name)
        else:
            running_containers.append(status.name)

    """
    Updating pod's containers resources if required
    """
    for index, container in enumerate(pod.spec.containers):
        if container.name in oomkilled_containers:
            req_memory = PodContainer.get_requests(
                job_event.spec.template.spec.containers[index]
            ).memory
            # checking if containers has reached the limit or not
            if req_memory < params.max_resource:
                keep_the_same = False
                containers.append(
                    increase_resource(
                        container,
                        params.max_resource,
                        params.increase_by,
                        keep_the_same,
                    )
                )
            else:
                finding.title = f"MAX REACHED"
                finding.add_enrichment(
                    [
                        MarkdownBlock(
                            f"*container request memory has reached the limit*\n```\n{container.name}\n```"
                        ),
                    ]
                )
                event.add_finding(finding)
                keep_the_same = True
                containers.append(
                    increase_resource(
                        container,
                        params.max_resource,
                        params.increase_by,
                        keep_the_same,
                    )
                )
        elif container.name in running_containers:
            keep_the_same = True
            containers.append(
                increase_resource(
                    container,
                    params.max_resource,
                    params.increase_by,
                    keep_the_same,
                )
            )

    job_spec = job_fields(job_event, containers)
    job_event.delete()
    job_spec.create()

    containers_memory_list = []

    # Getting information for finding
    for index, containers in enumerate(job_spec.spec.template.spec.containers):
        containers_memory_list.append(containers.name)
        containers_memory_list.append(containers.resources.requests["memory"])

    finding.title = f" JOB RESTARTED"
    finding.add_enrichment(
        [
            MarkdownBlock(
                f"*containers memory after restart*\n```\n{containers_memory_list}\n```"
            ),
        ]
    )
    event.add_finding(finding)


# Function to increase resource of the container
def increase_resource(container, max_resource, increase_by, keep_the_same):
    # Getting Container attributes
    container = Container(
        name=container.name,
        image=container.image,
        livenessProbe=container.livenessProbe,
        securityContext=container.securityContext,
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
        resources=memory_increment(
            container.resources, increase_by, max_resource, keep_the_same,
        )
        if (container.resources.limits and container.resources.requests)
        else None,
    )
    return container
 
# Function to increment in memory
def memory_increment(resources, increase_by, max_resource, keep_the_same):
    if keep_the_same:
        return resources
    else: 
        limits = resources.limits["memory"]
        reqests = resources.requests["memory"]

        # splitting num and str
        split_lim, lim_unit = split_num_and_str(limits)
        split_req, req_unit = split_num_and_str(reqests)

        split_increased_memory, split_increased_memory_unit = split_num_and_str(increase_by)
        
       
        
        # Checking if provided unit is same as job's memory unit
        if req_unit == split_increased_memory_unit:
      
            split_req = float(split_req) + float(split_increased_memory)

            if split_req > float(split_lim):
                split_lim = split_req
            if split_req > max_resource:
                split_req = max_resource
            return ResourceRequirements(
                limits={"memory": (str(split_lim) + lim_unit)},
                requests={"memory": (str(split_req) + req_unit)},
            )
        # else:
        #     logging.error(
        #         f"Provided unit is not same as that of Pod resource memory unit. Supported unit:{req_unit}"
        #     )
        #     return resources
        else:
            if req_unit == 'Mi':
              if split_increased_memory_unit == 'Gi':
                split_req = GiB(int(split_increased_memory)).to_MiB() + MiB(int(split_req))
    
                print(split_req)
            return resources



# # Function to increment in memory
# def memory_increment(resources, increase_by, max_resource, keep_the_same, unit):
#     if keep_the_same:
#         return resources
#     else: 
#         limits = resources.limits["memory"]
#         reqests = resources.requests["memory"]

#         # splitting num and str
#         split_lim, lim_unit = split_num_and_str(limits)
#         split_req, req_unit = split_num_and_str(reqests)

#         split_memory_increment, memory_unit = split_num_and_str(increase_by)
#         print(split_memory_increment)
#         print(memory_unit)

#         # Checking if provided unit is same as job's memory unit
#         if req_unit == unit:
#             split_req = float(split_req) + float(split_memory_increment)

#             if split_req > float(split_lim):
#                 split_lim = split_req
#             if split_req > max_resource:
#                 split_req = max_resource
#             return ResourceRequirements(
#                 limits={"memory": (str(split_lim) + lim_unit)},
#                 requests={"memory": (str(split_req) + req_unit)},
#             )
#         else:
#             logging.error(
#                 f"Provided unit is not same as that of Pod resource memory unit. Supported unit:{req_unit}"
#             )
#             return resources


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


# Function to get the job's field
def job_fields(job_event, container_list):
    # Getting job attributes
    job_spec = RobustaJob(
        metadata=ObjectMeta(
            name=job_event.metadata.name,
            namespace=job_event.metadata.namespace,
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
                    schedulerName=job_event.spec.template.spec.schedulerName,
                ),
            ),
        ),
    )
    return job_spec


def get_job_latest_pod(job: Job) -> Optional[RobustaPod]:
    if not job:
        return None

    job_labels = job.metadata.labels
    job_selector = f"{CONTROLLER_UID}={job_labels[CONTROLLER_UID]}"

    pod_list: List[RobustaPod] = PodList.listNamespacedPod(
        namespace=job.metadata.namespace, label_selector=job_selector
    ).obj.items
    pod_list.sort(key=lambda pod: pod.status.startTime, reverse=True)

    return pod_list[0] if pod_list else None