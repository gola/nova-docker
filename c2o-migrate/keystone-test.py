#!/usr/bin/python
from keystone import *

openstack = OpenstackManager("0s4c10ud", "http://10.27.2.1:35357/v2.0")

#user:
#1 user exist ?
#2 create user.
#3 user exist in tanent ?
#4 authorize tenant for user.
#####################################################
# 1
#if openstack.user_is_exist("sunbo"):
#    print "yes"
#else:
#    print "no"
# 2
#openstack.user_create("sunbo","111111","sunbo@cnsuning.com")
#
# 3
# make sure the tenant is exist, otherwise find the user in all tenant.
#if openstack.user_is_exist_in_tenant("admin", "admina"):
#   print "yes"
#else:
#   print "no"
#
# 4
#openstack.authorize_tenant_user_role("admin", "sunbo", "Member")
#
# othe test
#print openstack._user_name_to_id("sunbo")
#print openstack._list_user_in_tenant("test")


#roles: user's role exist in tenant./ add tenant role for user.
# 1. add role to user for a tenant.
#
# 1
#openstack.add_role_for_user_in_tenant("admin", "sunbo", "admin")
#other test
print openstack._role_name_to_id("admin")





#
#数据结构猜想
#sturct program{
#	char * name;
#	struct user **userlist；
#};
#
#struct user{
#	char *name;
#	enum ROLE *role; 
#};
#
#
#伪代码
#if not tenant_is_exist(...)
#	tenant_create(...)
#
#for user in user_list
#	if not user_is_exist(...)
#		user_create(...)
#	if user_is_exist_in_tenant(...)
#	    authorize_tenant_user_role(tenant,user,role[0])
#	if role_list_number > 1
#		add_user_role_in_project(....)







