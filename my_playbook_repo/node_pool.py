from email.policy import default
from robusta.api import *

@action
def node_pool(event: ExecutionBaseEvent): # We use EventEvent to get the event object.
    #actual_event = event.get_event()
    pod = pod_create()



# returns a pod that mounts the given persistent volume

def pod_create():
    reader_pod_spec = RobustaPod(
        apiVersion="v1",
        kind="Pod",
        metadata=ObjectMeta(
            name="volume-inspector",      
            namespace=default,
        ),
        spec=PodSpec(
            containers=[
                Container(
                    name="nginx",
                    image="nginx",
                  
                )
            ],
        )
    )
    reader_pod = reader_pod_spec.create()
    return reader_pod