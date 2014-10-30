#!/usr/bin/python

from keystoneclient.v2_0 import client as keystone_client
from glanceclient.v1 import client as glance_client

class OpenstackManager():
    """ The Openstack Manager for Migrate from cloudstack to openstack."""
    def __init__(self, user_name, user_password, tenant_name, auth_url, glance_endpoint):
        self.keystone = keystone_client.Client(username=user_name, password=user_password, tenant_name=tenant_name, auth_url=auth_url)
        self.token = self.keystone.auth_token
        self.glance = glance_client.Client(endpoint=glance_endpoint, token=self.token)
    
    def list(self):
        print self.glance.images.list()
        
    def image_create(self, disk_path, disk_name, disk_id, disk_format,container_format="bare", is_public=True):
        self.glance.images.create(data=open(disk_path,'rb'), name=disk_name, id=disk_id, disk_format=disk_format, container_format=container_format, is_public=is_public) 




glance = OpenstackManager("admin", "admin", "admin", "http://10.27.2.1:35357/v2.0/","http://10.27.2.1:9292")
glance.image_create("/root/centos6.5_x86-64.iso","Gukai", "55abe9f8-12df-41ea-ade1-b703c8ac0910", "iso")
