#!/usr/bin/python
from keystoneclient.v2_0 import client as keystone_client
from novaclient.v1_1 import client as nova_client
from cinderclient.v1 import client as cinder_client
from neutronclient.neutron import client as neutron_client
from keystoneclient.v2_0 import client as keystone_client
from glanceclient.v1 import client as glance_client

class OpenstackManager(object):
    """ The Openstack Manager for Migrate from cloudstack to openstack."""
    def __init__(self, user_name, user_password, tenant_name, auth_url, keystone_token):
        self.keystone = keystone_client.Client(token=keystone_token, endpoint=auth_url, tenant_name=tenant_name)
        self.nova = nova_client.Client(username=user_name, api_key=user_password, project_id=tenant_name, auth_url=auth_url)
        self.cinder = cinder_client.Client(username=user_name, api_key=user_password, project_id=tenant_name, auth_url=auth_url)
        self.neutron = neutron_client.Client('2.0', username=user_name, password=user_password, tenant_name=tenant_name, auth_url=auth_url)
        self.neutron.format = 'json'
        self._get_endpoint()
        self.glance = glance_client.Client(endpoint=self.glance_endpoint,username=user_name, password=user_password, tenant_name=tenant_name, auth_url=auth_url)
             
    
#################################################################
###############Keystone##########################################
################################################################
       
    ###################tenant-Manager###########################
    def tenant_is_exist(self, tenant_name): 
        tenant_list = self.keystone.tenants.list()
        for i in range(len(tenant_list)):
            if tenant_list[i].__dict__['name'] == tenant_name :
                return 1
        return 0

    def tenant_create(self, tenant_name, description=None, enabled=True):
        self.keystone.tenants.create(tenant_name, description, enabled)
    
    # fix me trave error.
    def _tenant_name_to_id(self, tenant_name):
        tenant_list = self.keystone.tenants.list()
        for i in range(len(tenant_list)):
            if tenant_list[i].__dict__['name'] == tenant_name :
                return tenant_list[i].__dict__['id']
    

    #list the user in tenant.
    def _list_user_in_tenant(self,tenant_name):
        tenant_id = self._tenant_name_to_id(tenant_name)
        return self.keystone.tenants.list_users(tenant_id)    

    def user_is_exist_in_tenant(self, tenant_name, user_name):
        user_list = self._list_user_in_tenant(tenant_name)
        for i in range(len(user_list)):
            if user_list[i].__dict__['name'] == user_name: 
                return 1
        return 0

    #def authorize_user_tenant()


    #######################User-Manager#############################
    def user_create(self, user_name, password, email=None):
        self.keystone.users.create(user_name, password, email)
    
        
 
    def user_is_exist(self, user_name):
        user_list = self.keystone.users.list()
        for i in range(len(user_list)):
            if user_list[i].__dict__['name'] == user_name :
                return 1
        return 0
         
    def _user_name_to_id(self, user_name):
        user_list = self.keystone.users.list()
        for i in range(len(user_list)):
            if user_list[i].__dict__['name'] == user_name :
                return user_list[i].__dict__['id']

    ####################Role-Manager##################################
    def authorize_tenant_user_role(self, tenant_name, user_name, role_name):
        tenant_id = self._tenant_name_to_id(tenant_name)
        user_id = self._user_name_to_id(user_name)
        role_id = self._role_name_to_id(role_name)
        self.keystone.tenants.add_user(tenant_id, user_id, role_id)

    def add_role_for_user_in_tenant(self, tenant_name, user_name, role_name):
        tenant_id = self._tenant_name_to_id(tenant_name)
        user_id = self._user_name_to_id(user_name)
        role_id = self._role_name_to_id(role_name)   
        self.keystone.roles.add_user_role(user_id, role_id, tenant_id)

    def _role_name_to_id(self, role_name):
        role_list = self.keystone.roles.list()
        for i in range(len(role_list)):
            if role_list[i].__dict__['name'] == role_name :
                return role_list[i].__dict__['id']

    # just for glance now.  
    def _get_endpoint(self):
        service_list = self.keystone.services.list()
        for i in range(len(service_list)):
            if service_list[i].type == "image":
                glance_id = service_list[i].id
        if glance_id == None:
            return
        endpoint_list = self.keystone.endpoints.list()
        for j in range(len(endpoint_list)):
            if endpoint_list[j].service_id == glance_id:
                self.glance_endpoint = endpoint_list[j].publicurl

############################################################################
##################NOVA######################################################
############################################################################
            
    def flavor_exist(self, cpu_num, ram_mb, root_disk_gb):
        nova_list = self.nova.flavors.list()
        for i in range(len(nova_list)):
            if nova_list[i].__dict__['vcpus'] == cpu_num and nova_list[i].__dict__['ram'] == ram_mb and nova_list[i].__dict__['disk'] == root_disk_gb:
                return 1
        return 0

    def flavor_create(self, cpu_num, ram_mb, root_disk_gb, flavor_name=None):
         # API: create(self, name, ram, vcpus, disk, flavorid="auto", ephemeral=0, swap=0, rxtx_factor=1.0, is_public=True):
        if flavor_name == None:
            cpu_str = '%d' % cpu_num
            ram_str = '%d' % ram_mb
            disk_str = '%d' % root_disk_gb
            flavor_name = cpu_str + 'C-' + ram_str + 'R-' + disk_str + 'D'
        print flavor_name
        self.nova.flavors.create(flavor_name, ram_mb, cpu_num, root_disk_gb)

#############################################################################
#####################Cinder##################################################
#############################################################################
    def volume_list(self):
        print self.cinder.volumes.list()
        

#############################################################################
#####################Neutron#################################################
#############################################################################
    def list_networks(self):
        print self.neutron.list_subnets()

#############################################################################
#####################Neutron#################################################
#############################################################################
    def image_list(self):
        print self.glance.images.list()

    def image_create(self, disk_path, disk_name, disk_id, disk_format,container_format="bare", is_public=True):
        self.glance.images.create(data=open(disk_path,'rb'), name=disk_name, id=disk_id, disk_format=disk_format, container_format=container_format, is_public=is_public)



if __name__ == '__main__':
    openstack = OpenstackManager("admin", "admin", "admin", "http://10.27.2.1:35357/v2.0", "0s4c10ud")

    print ###keystone-test###
    openstack._get_endpoint()
    print openstack.glance_endpoint
    print

    print ###nova-test####
    if openstack.flavor_exist(1,2048,20):
        print "yes"
    else:
        print "no"    

    print ###cinder-test###
    openstack.volume_list()

    print ###neutron-test###
    openstack.list_networks()

    print ###glance-test###
    openstack.image_list()
    
