#!/usr/bin/python
from openstack import *


openstack = OpenstackManager("admin", "admin", "admin", "http://10.27.2.1:35357/v2.0", "0s4c10ud")


##################################################################################
##############################Keystone############################################
##################################################################################


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
#print openstack._role_name_to_id("admin")

#other: get endpoint from keystone
#openstack._get_endpoint()
#print openstack.glance_endpoint


#########################################################################
########################NOVA############################################
########################################################################
# flavor
# 1: exist
# 2: create
########################################
# 1
#if openstack.flavor_exist(1,2,20):
#if openstack.flavor_exist(1,2048,20):
#   print "yes"
#else:
#   print "no"
# 2
#openstack.flavor_create(10000,120,119)


##########################################################################
#########################GLANCE###########################################
##########################################################################
#openstack.image_list()
#openstack.image_create("/root/centos6.5_x86-64.iso","Gukai", "55abe9f8-12df-41ea-ade1-b703c8ac0910", "iso")



##########################################################################
######################Neutron#############################################
#########################################################################
#openstack.list_networks()



##########################################################################
#####################Cinder###############################################
##########################################################################
#openstack.volume_list()














