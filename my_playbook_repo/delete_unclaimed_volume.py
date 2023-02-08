from robusta.api import *

@action
def delete_persistent_volume(event: PersistentVolumeEvent):

    """
    Deletes a persistent volume
    """

    if not event.get_persistentvolume():
        logging.info("Failed to get the pod for deletion")
        return
    pv = event.get_persistentvolume()
    pv_name = pv.metadata.name
    pv.delete()
    
    function_name = "delete_persistent_volume"
    finding = Finding(
        title=f"{pv_name} deleted.",
        source=FindingSource.MANUAL,
        aggregation_key=function_name,
        finding_type=FindingType.REPORT,
        failure=False,
    )
    finding.add_enrichment(
        [
            MarkdownBlock(
                f"*Persistent volume deleted"
            ),
        ]
    )
    event.add_finding(finding)