
from robusta.api import *
import google.auth
from google.cloud.container_v1 import ClusterManagerClient
from kubernetes import client


@action
def node_pool(event: ExecutionBaseEvent):

    credentials, project = google.auth.default(
        scopes=['https://www.googleapis.com/auth/cloud-platform'])

    credentials.refresh(credentials)
    cluster_manager = ClusterManagerClient(credentials=credentials)
    # cluster = cluster_manager.get_cluster(
    #     zone='us-central1-c', cluster_id='nodepool', project_id='wahajnodepool')

    print(credentials.scopes)

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
