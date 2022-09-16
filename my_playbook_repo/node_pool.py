from robusta.api import *
import google.cloud.container_v1 as container
from google.auth import compute_engine
from google.cloud.container_v1 import ClusterManagerClient
from kubernetes import client, config

@action
def node_pool(event: ExecutionBaseEvent):
    project_id = 'wahajnodepool'
    zone = 'us-central1-c'
    cluster_id = 'nodepool'

    credentials = compute_engine.Credentials()

    gclient: ClusterManagerClient = container.ClusterManagerClient(credentials=credentials)

    cluster = gclient.get_cluster(cluster_id='nodepool',zone='us-central1-c',project_id='wahajnodepool')
    cluster_endpoint = cluster.endpoint
    print("*** CLUSTER ENDPOINT ***")
    print(cluster_endpoint)

    cluster_master_auth = cluster.master_auth
    print("*** CLUSTER MASTER USERNAME PWD ***")
    cluster_username = cluster_master_auth.username
    cluster_password = cluster_master_auth.password
    print("USERNAME : %s - PASSWORD : %s" % (cluster_username, cluster_password))






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
