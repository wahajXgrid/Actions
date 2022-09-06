from robusta.api import *

@action
def report_scheduling_failure(event: EventEvent): # We use EventEvent to get the event object.
    actual_event = event.get_event()

    print(f"This print will be shown in the robusta logs={actual_event}")

    if actual_event.type.casefold() == f'Warning'.casefold() and \
        actual_event.reason.casefold() == f'FailedScheduling'.casefold() and \
        actual_event.involvedObject.kind.casefold() == f'Pod'.casefold():
        _report_failed_scheduling(event, actual_event.involvedObject.name, actual_event.message)

def _report_failed_scheduling(event: EventEvent, pod_name: str, message: str):
    custom_message = ""
    if "affinity/selector" in message:
        custom_message = "Your pod has a node 'selector' configured, which means it can't just run on any node. For more info, see: https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector"

    # this is how you send data to slack or other destinations

    # Note - is it sometimes better to create a Finding object instead of calling event.add_enrichment, but this is out of the scope of this tutorial

    event.add_enrichment([
        MarkdownBlock(f"Failed to schedule a pod named '{pod_name}'!\nerror: {message}\n\n{custom_message}"),
    ])
    
    
