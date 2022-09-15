
from robusta.api import *
from google.cloud.container import NodePool, GetClusterRequest, GetServerConfigRequest, GetNodePoolRequest
from googleapiclient import discovery
import google.auth


@action
# We use EventEvent to get the event object.
def node_pool(event: ExecutionBaseEvent):
    #actual_event = event.get_event()
    nodepool = GetNodePoolRequest()
    g_creds = google.auth.default()
    service = discovery.build('container', 'v1', credentials=g_creds)

    gcp_projects = ['wahajnodepool']

    for project in gcp_projects:
        request = service.projects().zones().clusters().list(projectId=project, zone='-')
        response = request.execute()

        if 'clusters' in response:
            for cluster in response['clusters']:
                print("%s,%s,%d" %
                      (project, cluster['name'], cluster['currentNodeCount']))
