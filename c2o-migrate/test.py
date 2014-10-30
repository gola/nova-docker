#!/usr/bin/python
from keystoneclient.v2_0 import client

token = '0s4c10ud'
endpoint = 'http://10.27.2.1:35357/v2.0'
tenant_name = 'admin'

keystone = client.Client(token=token, endpoint=endpoint, tenant_name=tenant_name)

print "**********************get        *************************************"
print keystone.tenants.get("admin")
print "***********************************************************************"
print

print "**********************list tenants*************************************"
print keystone.tenants.list()
print "***********************************************************************"
print

print "**********************list users*************************************"
print keystone.tenants.list_users('admin')
print "***********************************************************************"
print

#test
#tenant_list()

#def create(self, tenant_name, description=None, enabled=True, **kwargs):
#keystone
