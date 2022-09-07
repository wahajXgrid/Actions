from robusta.api import *

@action
def print_cluster_role_bindings(event: ExecutionBaseEvent):

    bindings: List[ClusterRoleBinding] = ClusterRoleBindingList.listClusterRoleBinding().obj.items
    roles: List[ClusterRole] = ClusterRoleList.listClusterRole().obj.items
    print(f"bindings {bindings}")
    print(f"roles {roles}")