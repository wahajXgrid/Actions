


from urllib import request
from robusta.api import *


class IncreaseResources(ActionParams):
   increase_to: Optional[float] = 1
   max_resource: float
     

@action
def job_restart(event: JobEvent,params: IncreaseResources):
    job_event = event.get_job()
    max_res,mem = split_num_and_str(job_event.spec.template.spec.containers[0].resources.requests['memory'])
    if float(max_res) < params.max_resource:
        
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

        job_event = event.get_job()
        pod = get_job_pod(event.get_job().metadata.namespace,
                            event.get_job().metadata.name)
        
        status_flag = True
        # # for multi-containers
        # for status in pod.status.containerStatuses:
        #     if status.state.terminated.reason == 'OOMKilled':
        #         status_flag = True
        #         break

        if status_flag:
            print("han bhai theek hy")         
            container_list = get_container_list(
                job_event.spec.template.spec.containers , increase_to=params.increase_to)
                
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
        print('max reached')
        function_name = "job_restart"
        finding = Finding(
            title=f"MAX REACHED",
            source=FindingSource.MANUAL,
            aggregation_key=function_name,
            finding_type=FindingType.REPORT,
            failure=False,
        )
        job_temp = event.get_job()

        finding.add_enrichment(
            [
                MarkdownBlock(
                    f"*max*reached*\n```\n{job_temp}\n```"
                ),
            ]
        )
        event.add_finding(finding)
      

def increase_resource(resource,increase_to):
    limits = resource.limits['memory']
    reqests = resource.requests['memory']
    
   
    split_lim,lim_unit = split_num_and_str(limits)
    split_req,req_unit = split_num_and_str(reqests)
    print(split_req)
    print(increase_to)
    split_req = float(split_req) + float(increase_to)
    print(split_req)
    if(split_req > float(split_lim)):
        split_lim = split_req    
    
    return ResourceRequirements(limits={"memory" : (str(split_lim)+lim_unit)},requests={"memory": (str(split_req)+req_unit)})
    

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
            resources = increase_resource(container.resources,increase_to) if (container.resources.limits and container.resources.requests)  else None  
        ))
    return containers_list

def get_job_pod(namespace, job):
    pod_list = PodList.listNamespacedPod(namespace).obj
    for pod in pod_list.items:
        if pod.metadata.name.startswith(job):   
            return pod

def split_num_and_str(num_str:str):
     
    num = ''
    index=None
    for ind,char in enumerate(num_str):
       if char.isdigit() or char is '.':
         num = num+char
       else:
         index =ind
         break
    return num,num_str[index:]