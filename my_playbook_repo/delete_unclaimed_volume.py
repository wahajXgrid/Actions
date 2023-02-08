from robusta.api import *

@action
def delete_unclaimed_volume(event: PersistentVolumeEvent):

    """
    Deletes a persistent volume
    """
    if not event.get_persistentvolume():
        logging.info("Failed to get the pod for deletion")
        return
    event.get_persistentvolume().delete()
    # if not event.get_pod():
    #     logging.info("Failed to get the pod for deletion")
    #     return

    # event.get_pod().delete()




    function_name = "delete_unclaimed_volume"
    finding = Finding(
        title=f"AD",
        source=FindingSource.MANUAL,
        aggregation_key=function_name,
        finding_type=FindingType.REPORT,
        failure=False,
    )
    finding.add_enrichment(
        [
            MarkdownBlock(
                f"*containers memory after restart"
            ),
        ]
    )
    event.add_finding(finding)