#    Copyright 2010 United States Government as represented by the
#    Administrator of the National Aeronautics and Space Administration.
#    All Rights Reserved.
#    Copyright (c) 2010 Citrix Systems, Inc.
#    Copyright (c) 2011 Piston Cloud Computing, Inc
#    Copyright (c) 2011 OpenStack Foundation
#    (c) Copyright 2013 Hewlett-Packard Development Company, L.P.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import sys
import commands

from nova import utils


def execute(*args, **kwargs):
    return utils.execute(*args, **kwargs)

# add by liuhaibin for get cpu information 2016-03-01
def get_cpu_info():
    """Get host cpu info .. add by syswin liuhaibin"""
    cpu_info = {}   
    out, err = execute("lscpu", run_as_root=True)
    out_ret = out.split('\n')
    cpu_info["arch"] = out_ret[0].split(':')[1].lstrip()
    cpu_info["vendor"]  = out_ret[9].split(':')[1].lstrip()
    cpu_info["cpus"] = out_ret[3].split(':')[1].lstrip()
    cpu_info["socket"] = out_ret[7].split(':')[1].lstrip()
    cpu_info["core_per_socket"] = out_ret[6].split(':')[1].lstrip()
    cpu_info["thread_per_core"] = out_ret[5].split(':')[1].lstrip()
    cpu_info["numa_nodes"] = out_ret[8].split(':')[1].lstrip()
    cpu_info["cpu_mhz"] = out_ret[13].split(':')[1].lstrip()
    cpu_info["virtualization"] = out_ret[15].split(':')[1].lstrip()
    out_version, err = execute("dmidecode", "-t", "processor", run_as_root=True)
    status, output = commands.getstatusoutput("echo '%s'|grep Version|awk -F':' 'NR==1 {print $2}'"%(out_version))
    cpu_info["version"] = output.lstrip()
    return cpu_info


# add by liuhaibin for get memory information 2016-03-01
def get_mem_info():
    """Get host memory info .. add by syswin liuhaibin"""
    mem_info = {}
    status, output_total = commands.getstatusoutput("free -g|awk 'NR==2{print $2}'")
    status, output_free = commands.getstatusoutput("free -g|awk 'NR==3{print $4}'")
    mem_info["total"] = output_total
    mem_info["free"] = output_free
    out_mem, err = execute("dmidecode", "-t", "memory", run_as_root=True)
    
    mem_info["total_slots"] = commands.getstatusoutput("echo '%s' |grep 'Memory Device'|wc -l" %(out_mem))[1]
    mem_info["unused_slots"] = commands.getstatusoutput("echo '%s' |grep 'Rank: Unknown'|wc -l" %(out_mem))[1]
    
    return mem_info

   
# add by liuhaibin for get disk information 2016-03-01
def get_disk_info():
    """Get host disk info ... add by syswin liuhaibin"""
    disk_info = {}
    out_vendor, err = execute("dmidecode", "-t", "chassis", run_as_root=True)
    status, output = commands.getstatusoutput("echo '%s' | grep Manufacturer|awk '{print $2}'"%(out_vendor))
    disk_info["disk_map"] = []
    disk_info["disk_size"] = []
    disk_info["disk_type"] = []
    disk_info["disk_state"] = []
    
    if output == "Inspur":
        out_disk, err = execute("storcli64", "/c0/eall/sall", "show", run_as_root=True)
        output_disk = commands.getstatusoutput("echo '%s'|grep -A 10  EID:Slt|sed -n '1,2!{$!p}'"%(out_disk))[1]
        disk_info["num"] = commands.getstatusoutput("echo '%s' |wc -l" %(output_disk))[1]
        for i in range(1,int(disk_info["num"])+1):
            status, output_map = commands.getstatusoutput("echo '%s'|sed -n $'%s',1p|awk '{print $1}'" %(output_disk,i))
            disk_info["disk_map"].append(output_map)
            status, output_size = commands.getstatusoutput("echo '%s'|sed -n $'%s',1p|awk '{print $5}'" %(output_disk,i))
            disk_info["disk_size"].append(output_size)
            status, output_type = commands.getstatusoutput("echo '%s'|sed -n $'%s',1p|awk '{print $7}'" %(output_disk,i))
            disk_info["disk_type"].append(output_type)
            status, output_state = commands.getstatusoutput("echo '%s'|sed -n $'%s',1p|awk '{print $3}'" %(output_disk,i))
            disk_info["disk_state"].append(output_state)
        
    elif output == "HP":
        out_disk, err = execute("hpssacli", "controller", "slot=0", "physicaldrive", "all", "show", "status", run_as_root=True)
        output_disk = commands.getstatusoutput("echo '%s'|grep physicaldrive"%(out_disk))[1]
        disk_info["num"] = commands.getstatusoutput("echo '%s' |wc -l" %(output_disk))[1]
        for i in range(1,int(disk_info["num"])+1):
            status, output_map = commands.getstatusoutput("echo '%s'|sed -n $'%s',1p|awk '{print $2}'" %(output_disk,i))
            disk_info["disk_map"].append(output_map)
            status, output_size = commands.getstatusoutput("echo '%s'|sed -n $'%s',1p|awk '{print $7}'" %(output_disk,i))
            disk_info["disk_size"].append(output_size)
            disk_info["disk_type"].append("")
            status, output_state = commands.getstatusoutput("echo '%s'|sed -n $'%s',1p|awk '{print $9}'" %(output_disk,i))
            disk_info["disk_state"].append(output_state)
       
    else:
        pass
    return disk_info
    

# add by liuhaibin for get bios information 2016-03-01
def get_bios_info():
    """Get host bios info .. add by syswin liuhaibin"""
    bios_info = {}
    output, err = execute("dmidecode", "-t", "bios", run_as_root=True)
    bios_info["vendor"] = commands.getstatusoutput("echo '%s' |grep Vendor|awk -F':' '{print $2}'" %(output))[1].lstrip()
    bios_info["version"] = commands.getstatusoutput("echo '%s' |grep Version|awk -F':' '{print $2}'" %(output))[1].lstrip()
    bios_info["runtime_size"] = commands.getstatusoutput("echo '%s' |grep Runtime|awk '{print $3}'" %(output))[1]
    bios_info["rom_size"] = commands.getstatusoutput("echo '%s' |grep 'ROM Size'|awk '{print $3}'" %(output))[1]
    return bios_info
 

# add by liuhaibin for get chassis information 2016-03-01
def get_chassis_info():
    """Get host chassis info ... add by syswin liuhaibin"""
    chassis_info = {}
    output, err = execute("dmidecode", "-t", "chassis", run_as_root=True)
    chassis_info["vendor"] = commands.getstatusoutput("echo '%s' |grep Manufacturer|awk '{print $2}'" %(output))[1]
    chassis_info["bootup_state"] = commands.getstatusoutput("echo '%s' |grep Boot-up|awk '{print $3}'" %(output))[1]
    chassis_info["power_supply_state"] = commands.getstatusoutput("echo '%s' |grep Supply |awk '{print $4}'" %(output))[1]
    chassis_info["thermal_state"] = commands.getstatusoutput("echo '%s' |grep Thermal |awk '{print $3}'" %(output))[1]
    if chassis_info["vendor"] == "Inspur":
        output, err = execute("ipmitool", "sensor", run_as_root=True)
        chassis_info["total_power"] = commands.getstatusoutput("echo '%s'|grep Total_Power|awk '{print $3}'"%(output))[1]
        chassis_info["power1"] = "0"
        chassis_info["power2"] = "0"
        
    elif chassis_info["vendor"] == "HP":
        output1, err = execute("ipmitool", "sensor", run_as_root=True)
        output2, err = execute("ipmitool", "sensor", run_as_root=True)
        chassis_info["power1"] = commands.getstatusoutput("echo '%s'|grep 'Power Supply 1'|awk '{print $5}'"%(output1))[1]
        chassis_info["power2"] = commands.getstatusoutput("echo '%s'|grep 'Power Supply 2'|awk '{print $5}'"%(output2))[1]
        total = float(chassis_info["power1"]) + float(chassis_info["power2"])
        chassis_info["total_power"] = str(total)
       
    else:
        chassis_info["total_power"] = "0"
        chassis_info["power1"] = "0"
        chassis_info["power2"] = "0"
    
 
    return chassis_info


# add by liuhaibin for get software information 2016-03-01
def get_software_info():
    """Get software info, such as libvirt,kernel etc ..add by syswin liuhaibin"""
   
    soft_info={}
    out_kernel, err = execute("uname", "-r", run_as_root=True)
    soft_info["kernel_version"] = out_kernel[:-1]
    out_libvirt, err = execute("libvirtd", "--version", run_as_root=True)
    soft_info["libvirt_version"] = out_libvirt[:-1]
    out_qemu, err = execute("qemu-kvm", "--version", run_as_root=True)
    soft_info["qemu_version"] = out_qemu[:-1]
    soft_info["python_version"] = sys.version.split('\n')[0]
    out_system, err = execute("cat", "/etc/issue", run_as_root=True)
    list_system = out_system.split('\n')
    soft_info["system"] = list_system[0]
    return soft_info
