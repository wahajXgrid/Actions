
from robusta.api import *
from googleapiclient import discovery
import google.auth


@action
def node_pool(event: ExecutionBaseEvent):
    
    g_creds = google.auth.default()
    service = discovery.build('container', 'v1', credentials=g_creds)

    gcp_projects = ['wahajnodepool']
    print(service)
    # for project in gcp_projects:
    #     request = service.projects().zones().clusters().list(projectId=project, zone='-')
    #     response = request.execute()

    #     if 'clusters' in response:
    #         for cluster in response['clusters']:
    #             print("%s,%s,%d" %
    #                   (project, cluster['name'], cluster['currentNodeCount']))
