#!/usr/bin/python
from nova import utils
from novadocker.virt.docker import hostinfo

#def get_cpu_info():
#    with open('/proc/cpuinfo') as f:
#       pcpu_total = 0
#       m = f.read().split()
#       for i in range(len(m)):
#           if m[i] == 'processor':
#               pcpu_total = pcpu_total + 1
#    return pcpu_total if pcpu_total > 1 else 1


class CpusetStatsMap(object):
    """ get cpuset stats """

    def __init__(self):
        self.container_list=[]
        self.cpu_num = hostinfo.get_cpu_info()
        self.cpu_map = {}
        for i in range(self.cpu_num):
            cpu_name = "cpu" + str(i)
            self.cpu_map[cpu_name] = 0

    def _get_container_list(self, all=False):
        if all:
            self.container_list = utils.execute('docker', 'ps', '--all', '-q', '--no-trunc')[0].split('\n')
        else:
            self.container_list = utils.execute('docker', 'ps', '-q', '--no-trunc')[0].split('\n')
        self.container_list.remove('')

    def _get_cpuset_str(self, container_id):
         cgroup_path = "docker/" + str(container_id)
         cpuset_str = utils.execute('cgget', '-v', '-r', 'cpuset.cpus', cgroup_path)[0].split('\n')[1]
         return cpuset_str

    def _push_in_map(self, cpu_list):
        for cpu in cpu_list:
            cpu_key = "cpu" + cpu
            self.cpu_map[cpu_key] = self.cpu_map[cpu_key] + 1

    def get_map(self):
        self._get_container_list(False)
        for id in self.container_list:
            cn_cpu_str = self._get_cpuset_str(id)
            cn_cpu_list = parse_cpuset()
            cn_cpu_list.parse(cn_cpu_str)
            self._push_in_map(cn_cpu_list.get_cpu_list())
        return self.cpu_map

    def less_set_cpus(self, num):
        ret_cpus = []
        less_set_list = sorted(self.cpu_map.items(), key=lambda d:d[1], reverse=False)[0:num]
        for cpu in less_set_list:
            ret_cpus.append(cpu[0])

        return ret_cpus

    def print_info(self):
        #print self.container_list
        print self.cpu_map



class parse_cpuset(object):
    """parse cpuset config to a list"""

    def __init__(self):
        self.first_num = ''
        self.sec_num = ''
        self.sec_mark = False
        self.cpu_list = []

    def _cl_swap_info(self):
        self.first_num = ''
        self.sec_num = ''
        self.sec_mark = False

    def _append_cpu_list(self):
        if self.sec_mark:
            for i in range(int(self.first_num), int(self.sec_num)+1):
                self.cpu_list.append(str(i))
            self._cl_swap_info()
        else:
            self.cpu_list.append(self.first_num)
            self._cl_swap_info()

    def parse(self, cpuset_str):
        self._cl_swap_info()
        for chr in cpuset_str:
            if chr.isdigit():
                if self.sec_mark:
                    self.sec_num = self.sec_num + chr
                else:
                    self.first_num = self.first_num + chr
            elif chr == "-":
                self.sec_mark = True
            elif chr ==",":
                self._append_cpu_list()

        self._append_cpu_list()

    def get_cpu_list(self):
        return self.cpu_list

if __name__ == '__main__':
    cpustats = CpusetStatsMap()
    cpustats.get_map()
    cpustats.print_info()
    print cpustats.less_set_cpus(2)
