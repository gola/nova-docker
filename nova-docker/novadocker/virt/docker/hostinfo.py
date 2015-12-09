# Copyright (c) 2013 dotCloud, Inc.
# All Rights Reserved.
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
import string


def get_disk_usage(docker_info):
    driver_info = docker_info['DriverStatus']
    data_total_num = 0
    data_used_num = 0
    data_total_unit = ''
    data_used_unit = ''

    for key,value in driver_info:
        if not cmp(key, 'Data Space Total'):
            data_total_raw = value.split()
            data_total_num = string.atof(data_total_raw[0])
            data_total_unit = data_total_raw[1]
        elif not cmp(key, 'Data Space Used'):
            data_used_raw = value.split()
            data_used_unit = data_used_raw[1]
            data_used_num = string.atof(data_used_raw[0])

    if data_total_unit == 'TB':
        data_total = data_total_num * 1024 * 1024 * 1024 * 1024
    elif data_total_unit == 'GB':
        data_total = data_total_num * 1024 * 1024 * 1024
    elif data_total_unit == 'MB':
        data_total = data_total_num * 1024 * 1024
    elif data_total_unit == 'KB':
        data_total = data_total_num * 1024
    else:
        data_total = 0

    if data_used_unit == 'TB':
        data_used = data_used_num * 1024 * 1024 * 1024 * 1024
    elif data_used_unit == 'GB':
        data_used = data_used_num * 1024 * 1024 * 1024
    elif data_used_unit == 'MB':
        data_used = data_used_num * 1024 * 1024
    elif data_used_unit == 'KB':
        data_used = data_used_num * 1024
    else:
        data_used = 0

    data_total = int(data_total)
    data_used = int(data_used)

    return {
        'total': data_total,
        'available': data_total - data_used,
        'used': data_used
    }


def get_memory_usage():
    with open('/proc/meminfo') as f:
        m = f.read().split()
        idx1 = m.index('MemTotal:')
        idx2 = m.index('MemFree:')
        idx3 = m.index('Buffers:')
        idx4 = m.index('Cached:')

        total = int(m[idx1 + 1])
        avail = int(m[idx2 + 1]) + int(m[idx3 + 1]) + int(m[idx4 + 1])

    return {
        'total': total * 1024,
        'used': (total - avail) * 1024
    }

def get_cpu_info():
    with open('/proc/cpuinfo') as f:
       pcpu_total = 0
       m = f.read().split()
       for i in range(len(m)):
           if m[i] == 'processor':
               pcpu_total = pcpu_total + 1
    return pcpu_total if pcpu_total > 1 else 1

def get_mounts():
    with open('/proc/mounts') as f:
        return f.readlines()


def get_cgroup_devices_path():
    for ln in get_mounts():
        fields = ln.split(' ')
        if fields[2] == 'cgroup' and 'devices' in fields[3].split(','):
            return fields[1]
