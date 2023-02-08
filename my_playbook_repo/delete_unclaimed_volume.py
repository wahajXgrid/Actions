from robusta.api import *

@action
def delete_unclaimed_volume(event: PodEvent):
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