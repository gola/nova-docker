#!/usr/bin/python
from keystoneclient.v2_0 import client



class OpenstackManager():
    """ The Openstack Manager for Migrate from cloudstack to openstack."""
    def __init__(self, token, endpoint, tenant_name="admin"):
        self.client = client.Client(token=token, endpoint=endpoint, tenant_name=tenant_name)
   
    #####################Tenant Manager########################
    def tenant_is_exist(self, tenant_name): 
        tenant_list = self.client.tenants.list()
        for i in range(len(tenant_list)):
            if tenant_list[i].__dict__['name'] == tenant_name :
                return 1
        return 0

    def tenant_create(self, tenant_name, description=None, enabled=True):
        self.client.tenants.create(tenant_name, description, enabled)
    
    # fix me trave error.
    def _tenant_name_to_id(self, tenant_name):
        tenant_list = self.client.tenants.list()
        for i in range(len(tenant_list)):
            if tenant_list[i].__dict__['name'] == tenant_name :
                return tenant_list[i].__dict__['id']
    

    #list the user in tenant.
    def _list_user_in_tenant(self,tenant_name):
        tenant_id = self._tenant_name_to_id(tenant_name)
        return self.client.tenants.list_users(tenant_id)    

    def user_is_exist_in_tenant(self, tenant_name, user_name):
        user_list = self._list_user_in_tenant(tenant_name)
        for i in range(len(user_list)):
            if user_list[i].__dict__['name'] == user_name: 
                return 1
        return 0

    #def authorize_user_tenant()


    #######################User-Manager#############################
    def user_create(self, user_name, password, email=None):
        self.client.users.create(user_name, password, email)
    
    #def _list_user_all():
        
 
    def user_is_exist(self, user_name):
        user_list = self.client.users.list()
        for i in range(len(user_list)):
            if user_list[i].__dict__['name'] == user_name :
                return 1
        return 0
         
    def _user_name_to_id(self, user_name):
        user_list = self.client.users.list()
        for i in range(len(user_list)):
            if user_list[i].__dict__['name'] == user_name :
                return user_list[i].__dict__['id']

    def authorize_tenant_user_role(self, tenant_name, user_name, role_name):
        tenant_id = self._tenant_name_to_id(tenant_name)
        user_id = self._user_name_to_id(user_name)
        role_id = self._role_name_to_id(role_name)
        self.client.tenants.add_user(tenant_id, user_id, role_id)

    ########################Role-Manager############################## 
    def add_role_for_user_in_tenant(self, tenant_name, user_name, role_name):
        tenant_id = self._tenant_name_to_id(tenant_name)
        user_id = self._user_name_to_id(user_name)
        role_id = self._role_name_to_id(role_name)   
        self.client.roles.add_user_role(user_id, role_id, tenant_id)

    def _role_name_to_id(self, role_name):
        role_list = self.client.roles.list()
        for i in range(len(role_list)):
            if role_list[i].__dict__['name'] == role_name :
                return role_list[i].__dict__['id']
    #####################################################################
    # just for glance and neutron now.  
    def _get_endpoint(self):
        service_list = self.client.services.list()
        for i in range(len(service_list)):
            if service_list[i].type == "image":
                glance_id = service_list[i].id
        if glance_id == None:
            return

        endpoint_list = self.client.endpoints.list()
        for j in range(len(endpoint_list)):
            if endpoint_list[j].service_id == glance_id:
                self.glance_endpoint = endpoint_list[j].publicurl
                         

        

if __name__ == '__main__':
    keystone = OpenstackManager("0s4c10ud", "http://10.27.2.1:35357/v2.0")


    keystone._get_endpoint()
    print keystone.glance_endpoint
