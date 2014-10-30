#!/usr/bin/python
from novaclient.v1_1 import client as nova_client



class OpenstackManager():
    """ The Openstack Manager for Migrate from cloudstack to openstack."""
    def __init__(self, user_name, user_password, tenant_name, auth_url):
        self.nova = nova_client.Client(username=user_name, api_key=user_password, project_id=tenant_name, auth_url=auth_url)
    
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



nova = OpenstackManager("admin","admin","admin", "http://10.27.2.1:35357/v2.0/")

# flavor
# 1: exist
# 2: create
########################################
# 1
#if nova.flavor_exist(1,2,20):
#if nova.flavor_exist(1,2048,20):
#   print "yes"
#else:
#   print "no"
# 2
#nova.flavor_create(10000,120,119)









