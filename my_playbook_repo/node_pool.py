
from robusta.api import *
from google.auth import default
from google.auth.transport.requests import Request
from google.cloud.container_v1 import ClusterManagerClient
from kubernetes import client


@action
def node_pool(event: ExecutionBaseEvent):

    credentials, project = default(
        scopes=['https://www.googleapis.com/auth/cloud-platform'])

    credentials.refresh(Request())
    cluster_manager = ClusterManagerClient(credentials=credentials)
    cluster = cluster_manager.get_cluster(
        zone='us-central1-c', cluster_id='nodepool', project_id='wahajnodepool')

    config = client.Configuration()
    config.host = f'https://{cluster.endpoint}:443'
    config.verify_ssl = False
    config.api_key = {"authorization": "Bearer " + credentials.token}
    config.username = credentials._service_account_email

    client.Configuration.set_default(config)

    kub = client.CoreV1Api()
    print(kub.list_pod_for_all_namespaces(watch=False))
