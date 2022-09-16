from robusta.api import *
from google.auth import compute_engine
from google.cloud.container_v1 import ClusterManagerClient
from kubernetes import client

@action
def node_pool(event: ExecutionBaseEvent):
    project_id = "wahajnodepool"
    zone = "us-central1-c"
    cluster_id = "nodepool"

    credentials = compute_engine.Credentials()

    cluster_manager_client = ClusterManagerClient(credentials=credentials)
    cluster = cluster_manager_client.get_cluster(name=f'projects/{project_id}/locations/{zone}/clusters/{cluster_id}')

    configuration = client.Configuration()
    configuration.host = f"https://{cluster.endpoint}:443"
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": "Bearer " + credentials.token}
    client.Configuration.set_default(configuration)

    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    pods = v1.list_pod_for_all_namespaces(watch=False)
    for i in pods.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))






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
