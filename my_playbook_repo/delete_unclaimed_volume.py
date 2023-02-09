from robusta.api import *


@action
def delete_persistent_volume(event: PersistentVolumeEvent):

    """
    Deletes a persistent volume
    """

    # Check if the persistent volume is present
    if not event.get_persistentvolume():
        # Log an error message if the volume is not found
        logging.info("Failed to get the pod for deletion")
        return
    # Get the persistent volume
    pv = event.get_persistentvolume()
    # Get the name of the persistent volume
    pv_name = pv.metadata.name
    pv.delete()

    # Create a Finding object to store and send the details of the deleted volume
    function_name = "delete_persistent_volume"
    finding = Finding(
        title=f"*Persistent volume deleted",
        source=FindingSource.MANUAL,
        aggregation_key=function_name,
        finding_type=FindingType.REPORT,
        failure=False,
    )
    # Add a MarkdownBlock to the finding object to display the deleted volume name
    finding.add_enrichment(
        [
            MarkdownBlock(f"{pv_name} deleted."),
        ]
    )
    event.add_finding(finding)
