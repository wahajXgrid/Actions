from robusta.api import *



@action
def cluster_permissions_watcher(event: ClusterRoleBindingEvent):
    
    """
    This action track changes to ClusterRoleBindings to stay on top of who has what permissions.
    """
    function_name = "cluster_permissions_watcher"
    # https://docs.robusta.dev/master/developer-guide/actions/findings-api.html
    finding = Finding(
        title=f"ClusterRoleBinding Permission Status",
        source=FindingSource.MANUAL,
        aggregation_key=function_name,
        finding_type=FindingType.REPORT,
        failure=False,
    )
    clusterrolebinding = event.get_clusterrolebinding()
    print(clusterrolebinding)


