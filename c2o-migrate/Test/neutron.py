from keystoneclient.v2_0 import client as keystone_client
from glanceclient.v1 import client as glance_client
from neutronclient.neutron import client as neutron_client

class OpenstackManager():
    """ The Openstack Manager for Migrate from cloudstack to openstack."""
    def __init__(self, user_name, user_password, tenant_name, auth_url, neutron_endpoint):
        self.keystone = keystone_client.Client(username=user_name, password=user_password, tenant_name=tenant_name, auth_url=auth_url)
        self.token = self.keystone.auth_token
        print self.token
        #self.neutron=neutron_client.Client('2.0', endpoint=neutron_endpoint, auth_token=self.token, auth_url=auth_url, tenant_name=tenant_name)
        self.neutron=neutron_client.Client('2.0', endpoint_url=neutron_endpoint, token=self.token)
        self.neutron.format="json"

    def list_networks(self):
        print self.neutron.list_subnets()


neutron = OpenstackManager("admin", "admin", "admin", "http://10.27.2.1:35357/v2.0/", "http://10.27.2.1:9696")
neutron.list_networks()
