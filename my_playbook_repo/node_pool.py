
from robusta.api import *
import google.auth
from google.cloud.container_v1 import ClusterManagerClient
from kubernetes import client


@action
def node_pool(event: ExecutionBaseEvent):

    credentials, project = google.auth.default(
        scopes=['https://www.googleapis.com/auth/cloud-platform'])

    credentials.refresh(google.auth.transport.requests.Request())
    cluster_manager = ClusterManagerClient(credentials=credentials)
    cluster = cluster_manager.get_cluster(
        zone='us-central1-c', project_id=project, name='nodepool')
    
    config = client.Configuration()
    config.host = f'https://{cluster.endpoint}:443'
    config.verify_ssl = False
    config.api_key = {"authorization": "Bearer " + credentials.token}
    config.username = credentials._service_account_email

    client.Configuration.set_default(config)

    kub = client.CoreV1Api()
    print(kub.list_pod_for_all_namespaces(watch=False))
    # #g_creds = google.auth.default()
    # service = discovery.build('container', 'v1', credentials=g_creds)

    # gcp_projects = ['wahajnodepool']
    # print(service)
    # # for project in gcp_projects:
    # #     request = service.projects().zones().clusters().list(projectId=project, zone='-')
    # #     response = request.execute()

    # #     if 'clusters' in response:
    # #         for cluster in response['clusters']:
    # #             print("%s,%s,%d" %
    # #                   (project, cluster['name'], cluster['currentNodeCount']))
