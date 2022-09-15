
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

    print(credentials.client_id)
    print(f"*******\n {credentials.info}")

    print(f"*******\n {credentials.id_token}")

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
