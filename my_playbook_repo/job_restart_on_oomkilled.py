from robusta.api import *
import bitmath as bitmath

CONTROLLER_UID = "controller-uid"


class IncreaseResources(ActionParams):

    """
    :var increase_by: (optional).Users will specify how much they want to increase in each restart.
    :var max_resource: This variable prevent an infinite loop of job's pod crashing and getting more memory.The action won't increase the memory again when the "Max" limit reached.
    """

    increase_by: Optional[str] = 1
    max_resource: str


@action
def job_restart_on_oomkilled(event: JobEvent, params: IncreaseResources):
    """
    This action will run when job failed with oomkilled
    """
    function_name = "job_restart_on_oomkilled"
    finding = Finding(
        title=f"JOB RESTARTED",
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

            req_memory = bitmath.parse_string_unsafe(
                container.resources.requests["memory"]
            )

            max_resource = bitmath.parse_string_unsafe(params.max_resource)

            if req_memory < max_resource:

                keep_the_same = False
                containers.append(
                    increase_resource(
                        container,
                        max_resource,
                        params.increase_by,
                        keep_the_same,
                    )
                )
            else:
                print("call")
                finding.title = f"MAX REACHED"
                finding.add_enrichment(
                    [
                        MarkdownBlock(
                            f"*container request memory has reached the limit*\n```\n{container.name}\n```"
                        ),
                    ]
                )

                keep_the_same = True
                containers.append(
                    increase_resource(
                        container,
                        max_resource,
                        params.increase_by,
                        keep_the_same,
                    )
                )
        elif container.name in running_containers:
            keep_the_same = True
            containers.append(
                increase_resource(
                    container,
                    max_resource,
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
            container.resources,
            increase_by,
            max_resource,
            keep_the_same,
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
        reqests = bitmath.parse_string_unsafe(resources.requests["memory"])
        limits = bitmath.parse_string_unsafe(resources.limits["memory"])
        increase_by = bitmath.parse_string_unsafe(increase_by)

        # if reqests.unit == increase_by.unit:
        #     reqests = reqests + increase_by
        #     if reqests > max_resource:
        #         reqests = max_resource
        #     if reqests > limits:
        #         limits = reqests
        #     print("call GB")
        #     print(str(limits.unit))
        #     return ResourceRequirements(
        #         limits={"memory": (str(limits.value) + str(limits.unit))},
        #         requests={"memory": (str(reqests.value) + str(reqests.unit))},
        #     )
        
        if reqests.unit == "MiB":
            if increase_by.unit == "Mi" or increase_by.unit == "MiB":
                reqests = reqests + increase_by
                if reqests > max_resource:
                    reqests = max_resource.to_MiB()
                if reqests > limits:
                    limits = reqests
                return ResourceRequirements(
                    limits={"memory": (str(limits.value) + "Mi")},
                    requests={"memory": (str(reqests.value) + "Mi")},
                )

            elif increase_by.unit == "Gi" or increase_by.unit == "GiB":
                reqests = increase_by.to_MiB() + reqests
                if reqests > max_resource:
                    reqests = max_resource.to_MiB()
                if reqests > limits:
                    limits = reqests
                return ResourceRequirements(
                    limits={"memory": (str(limits.value) + "Mi")},
                    requests={"memory": (str(reqests.value) + "Mi")},
                )

            elif increase_by.unit == "Ki" or increase_by.unit == "KiB":
                print("call me")
                reqests = increase_by.to_MiB() + reqests
                print(reqests)
                reqests = reqests.format("{value:.1f}")
                print(reqests)
                bitmath.MiB(int(float(reqests)))
                print(reqests)
                print(type(reqests))
                if reqests > max_resource:
                    print("no")
                    reqests = max_resource.to_MiB()
                if reqests > limits:
                    print("yes")
                    limits = reqests
                print(limits.value)
                print(reqests.value)
                return ResourceRequirements(
                    limits={"memory": (str(limits.value) + "Mi")},
                    requests={"memory": (str(reqests.value) + "Mi")},
                )

        if reqests.unit == "GiB":
            if increase_by.unit == "Mi" or increase_by.unit == "MiB":
                reqests = reqests + increase_by.to_GiB()
                if reqests > max_resource:
                    reqests = max_resource.to_GiB()
                if reqests > limits:
                    limits = reqests
                return ResourceRequirements(
                    limits={"memory": (str(limits.value) + "Gi")},
                    requests={"memory": (str(reqests.value) + "Gi")},
                )

            elif increase_by.unit == "Gi" or increase_by.unit == "GiB":
                reqests = increase_by + reqests
                if reqests > max_resource:
                    reqests = max_resource.to_GiB()
                if reqests > limits:
                    limits = reqests
                return ResourceRequirements(
                    limits={"memory": (str(limits.value) + "Gi")},
                    requests={"memory": (str(reqests.value) + "Gi")},
                )

            elif increase_by.unit == "Ki" or increase_by.unit == "KiB":
                reqests = increase_by.to_GiB() + reqests
                if reqests > max_resource:
                    reqests = max_resource.to_MiB()
                if reqests > limits:
                    limits = reqests
                return ResourceRequirements(
                    limits={"memory": (str(limits.value) + "Mi")},
                    requests={"memory": (str(reqests.value) + "Mi")},
                )
        # if existing_req_unit == "Gi":
        #     if (
        #         split_increased_memory_unit == "Mi"
        #         or split_increased_memory_unit == "MiB"
        #     ):
        #         existing_req_memory = bitmath.MiB(round(int(split_increased_memory))).to_GiB() + bitmath.GiB(
        #             int(existing_req_memory)
        #         )
        #         existing_req_memory = int(existing_req_memory)
        #         if existing_req_memory > int(existing_limit_memory):
        #             existing_limit_memory = existing_req_memory
        #         if existing_req_memory > max_resource:
        #             existing_req_memory = max_resource
        #         return ResourceRequirements(
        #             limits={"memory": (str(existing_limit_memory) + existing_lim_unit)},
        #             requests={"memory": (str(existing_req_memory) + existing_req_unit)},
        #         )

        #     elif (
        #         split_increased_memory_unit == "Ki"
        #         or split_increased_memory_unit == "KiB"
        #     ):
        #         existing_req_memory = bitmath.KiB(int(split_increased_memory)).to_GiB() + bitmath.GiB(
        #             int(existing_req_memory)
        #         )
        #         existing_req_memory = int(existing_req_memory)
        #         if existing_req_memory > int(existing_limit_memory):
        #             existing_limit_memory = existing_req_memory
        #         if existing_req_memory > max_resource:
        #             existing_req_memory = max_resource
        #         return ResourceRequirements(
        #             limits={"memory": (str(existing_limit_memory) + existing_lim_unit)},
        #             requests={"memory": (str(existing_req_memory) + existing_req_unit)},
        #         )

        # if existing_req_unit == "Ki":
        #     if (
        #         split_increased_memory_unit == "Mi"
        #         or split_increased_memory_unit == "MiB"
        #     ):
        #         existing_req_memory = bitmath.MiB(int(split_increased_memory)).to_KiB() + bitmath.KiB(
        #             int(existing_req_memory)
        #         )
        #         existing_req_memory = int(existing_req_memory)
        #         if existing_req_memory > int(existing_limit_memory):
        #             existing_limit_memory = existing_req_memory
        #         if existing_req_memory > max_resource:
        #             existing_req_memory = max_resource
        #         return ResourceRequirements(
        #             limits={"memory": (str(existing_limit_memory) + existing_lim_unit)},
        #             requests={"memory": (str(existing_req_memory) + existing_req_unit)},
        #         )
        #     elif (
        #         split_increased_memory_unit == "Gi"
        #         or split_increased_memory_unit == "GiB"
        #     ):
        #         existing_req_memory = bitmath.GiB(int(split_increased_memory)).to_KiB() + bitmath.KiB(
        #             int(existing_req_memory)
        #         )
        #         existing_req_memory = int(existing_req_memory)
        #         if existing_req_memory > int(existing_limit_memory):
        #             existing_limit_memory = existing_req_memory
        #         if existing_req_memory > max_resource:
        #             existing_req_memory = max_resource
        #         return ResourceRequirements(
        #             limits={"memory": (str(existing_limit_memory) + existing_lim_unit)},
        #             requests={"memory": (str(existing_req_memory) + existing_req_unit)},
        #         )


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
