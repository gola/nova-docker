#!/user/bin/python
from cinderclient.v1 import client as cinder_client


class OpenstackManager():
    """ The Openstack Manager for Migrate from cloudstack to openstack."""
    def __init__(self, user_name, user_password, tenant_name, auth_url):
        self.cinder = cinder_client.Client(username=user_name, api_key=user_password, project_id=tenant_name, auth_url=auth_url)

    def volume_list(self):
        print self.cinder.volumes.list()













cinder = OpenstackManager("admin","admin","admin", "http://10.27.2.1:35357/v2.0/")
cinder.volume_list()
