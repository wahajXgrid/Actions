from copy import copy
from pdb import Restart
from robusta.api import *



@action
def job_restart(event: JobEvent, params: EventEnricherParams):
    job_event = event.get_job().status.failed
    if job_event is not None:     
        print ("*****************")
        print("FAILED")
       
        pod = get_job_pod(event.get_job().metadata.namespace, event.get_job().metadata.name)
        print (pod.status.containerStatuses.reason)
        
    else:
        print ("*****************")
        print("Succeed")
    # job_spec = RobustaJob(
    #     metadata=ObjectMeta(
    #         name=job_event.metadata.name,
    #         namespace=job_event.metadata.namespace,
    #         labels=job_event.metadata.labels,
    #     ),
    #     spec=JobSpec(
    #         completions=job_event.spec.completions,
    #         parallelism=job_event.spec.parallelism,
    #         backoffLimit=job_event.spec.backoffLimit,
           
    #         activeDeadlineSeconds=job_event.spec.activeDeadlineSeconds,
            
    #         ttlSecondsAfterFinished=job_event.spec.ttlSecondsAfterFinished,
    #         template=PodTemplateSpec(
    #             spec=PodSpec(
    #                 containers=[Container(
    #                     name=job_event.spec.template.spec.containers[0].name,
    #                     image=job_event.spec.template.spec.containers[0].image,
    #                     args=job_event.spec.template.spec.containers[0].args,
    #                     command=job_event.spec.template.spec.containers[0].command,
    #                     env=job_event.spec.template.spec.containers[0].env,
    #                     envFrom=job_event.spec.template.spec.containers[0].envFrom,
    #                     imagePullPolicy=job_event.spec.template.spec.containers[0].imagePullPolicy,

    #                 ),
    #                 ],
    #             restartPolicy= job_event.spec.template.spec.restartPolicy
    #             ),
    #         ),

    #     ),
    # )
    # job_event.delete() 
    # job_spec.create()

def get_job_pod(namespace,job):
    pod_list = PodList.listNamespacedPod(namespace).obj
    for pod in pod_list.items:
        if pod.metadata.name.startswith(job): 
            return pod
    
    
    