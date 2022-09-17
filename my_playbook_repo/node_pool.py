from robusta.api import *
import pulumi
import pulumi_gcp as gcp

@action
def node_pool(event: ExecutionBaseEvent):
# Read in some configurable settings for our cluster.
# If nothing is set the specified default values will take effect.
    config = pulumi.Config()
    NODE_COUNT = config.get_int('node_count') or 1
    NODE_MACHINE_TYPE = config.get('node_machine_type') or 'e2-medium'
    MASTER_VERSION = config.get('master_version') or '1.21.14-gke.700'

    # Defining the GKE Cluster
    gke_cluster = gcp.container.Cluster('cluster-1', 
        name = "cluster-1",
        location = "us-central1",
        initial_node_count = NODE_COUNT,
        remove_default_node_pool = True,
        min_master_version = MASTER_VERSION,
    )

    # Defining the GKE Node Pool
    gke_nodepool = gcp.container.NodePool("nodepool-1",
        name = "nodepool-1",
        location = "us-central1",
        node_locations = ["us-central1-a"],
        cluster = gke_cluster.id,
        node_count = NODE_COUNT,
        node_config = gcp.container.NodePoolNodeConfigArgs(
            preemptible = False,
            machine_type = NODE_MACHINE_TYPE,
            disk_size_gb = 20,
            oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"],
            shielded_instance_config = gcp.container.NodePoolNodeConfigShieldedInstanceConfigArgs(
                enable_integrity_monitoring = True,
                enable_secure_boot = True
            )
        ),
        # Set the Nodepool Autoscaling configuration
        autoscaling = gcp.container.NodePoolAutoscalingArgs(
            min_node_count = 1,
            max_node_count = 3
        ),
        # Set the Nodepool Management configuration
        management = gcp.container.NodePoolManagementArgs(
            auto_repair  = True,
            auto_upgrade = True
        )
    )





# from robusta.api import *
# import google.cloud.container_v1 as container
# from google.auth import compute_engine
# from google.cloud.container_v1 import ClusterManagerClient
# from kubernetes import client, config

# @action
# def node_pool(event: ExecutionBaseEvent):
#     project_id = 'wahajnodepool'
#     zone = 'us-central1-c'
#     cluster_id = 'nodepool'

#     credentials = compute_engine.Credentials()
#     print("****",credentials)
    
    # gclient: ClusterManagerClient = container.ClusterManagerClient(credentials=credentials)

    # cluster = gclient.get_cluster(cluster_id='nodepool',zone='us-central1-c',project_id='wahajnodepool')
    # cluster_endpoint = cluster.endpoint
    # print("*** CLUSTER ENDPOINT ***")
    # print(cluster_endpoint)




# from robusta.api import *
# from google.auth import default
# from google.auth.transport.requests import Request
# from google.cloud.container_v1 import ClusterManagerClient
# from kubernetes import client


# @action
# def node_pool(event: ExecutionBaseEvent):

#     credentials, project = default(
#         scopes=['https://www.googleapis.com/auth/cloud-platform'])

#     credentials.refresh(Request())
#     cluster_manager = ClusterManagerClient(credentials=credentials)
#     print(cluster_manager.DEFAULT_ENDPOINT)
#     # cluster = cluster_manager.

#     # config = client.Configuration()
#     # config.host = f'https://{cluster.endpoint}:443'
#     # config.verify_ssl = False
#     # config.api_key = {"authorization": "Bearer " + credentials.token}
#     # config.username = credentials._service_account_email

#     # client.Configuration.set_default(config)

#     # kub = client.CoreV1Api()
#     # print(kub.list_pod_for_all_namespaces(watch=False))
