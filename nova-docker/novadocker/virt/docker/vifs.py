# Copyright (C) 2013 VMware, Inc
# Copyright 2011 OpenStack Foundation
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


from nova import exception
from nova.i18n import _
from nova.network import linux_net
from nova.network import manager
from nova.network import model as network_model
from nova.openstack.common import log as logging
from nova.openstack.common import processutils
from nova import utils
from novadocker.virt.docker import network
from oslo.config import cfg
import random

# We need config opts from manager, but pep8 complains, this silences it.
assert manager

CONF = cfg.CONF
CONF.import_opt('my_ip', 'nova.netconf')
CONF.import_opt('vlan_interface', 'nova.manager')
CONF.import_opt('flat_interface', 'nova.manager')

#CONF.import_opt('ovs_work_type','docker')
docker_opts = [
        cfg.StrOpt('ovs_work_type',
               default='direct',
               help='Type of OVS(direct/hybird), '
                    'direct is default,'
                    'hybird add an linux between ovs and container.'
                    'hybird only work if ovs_hybrid_plug set in port details ')
]
CONF.register_opts(docker_opts, 'docker')


LOG = logging.getLogger(__name__)


class DockerGenericVIFDriver(object):

    def plug(self, instance, vif):
        vif_type = vif['type']

        LOG.debug('plug vif_type=%(vif_type)s instance=%(instance)s '
                  'vif=%(vif)s',
                  {'vif_type': vif_type, 'instance': instance,
                   'vif': vif})

        if vif_type is None:
            raise exception.NovaException(
                _("vif_type parameter must be present "
                  "for this vif_driver implementation"))

        if vif_type == network_model.VIF_TYPE_BRIDGE:
            self.plug_bridge(instance, vif)
        elif vif_type == network_model.VIF_TYPE_OVS:
            self.plug_ovs(instance, vif)
        else:
            raise exception.NovaException(
                _("Unexpected vif_type=%s") % vif_type)

    def plug_ovs(self, instance, vif):
        if CONF.docker.ovs_work_type == "hybird" and  vif.is_hybrid_plug_enabled():
            LOG.debug('ovs type is hybird..')
            self.plug_ovs_hybird(instance, vif)
        else:
            LOG.debug('ovs type is direct')
            self.plug_ovs_bridge(instance, vif)

    def plug_ovs_bridge(self, instance, vif):
        if_local_name = 'tap%s' % vif['id'][:11]
        if_remote_name = 'ns%s' % vif['id'][:11]
        bridge = vif['network']['bridge']

        # Device already exists so return.
        if linux_net.device_exists(if_local_name):
            return
        undo_mgr = utils.UndoManager()

        try:
            utils.execute('ip', 'link', 'add', 'name', if_local_name, 'type',
                          'veth', 'peer', 'name', if_remote_name,
                          run_as_root=True)
            linux_net.create_ovs_vif_port(bridge, if_local_name,
                                          network.get_ovs_interfaceid(vif),
                                          vif['address'],
                                          instance['uuid'])
            utils.execute('ip', 'link', 'set', if_local_name, 'up',
                          run_as_root=True)
        except Exception:
            LOG.exception("Failed to configure network")
            msg = _('Failed to setup the network, rolling back')
            undo_mgr.rollback_and_reraise(msg=msg, instance=instance)

    def plug_ovs_hybird(self, instance, vif):
        iface_id = vif['id'][:11]
        if_local_name = 'tap%s' % iface_id
        if_remote_name = 'ns%s' % vif['id'][:11]
        v1_name = 'qvb%s' % iface_id
        v2_name = 'qvo%s' % iface_id
        if_bridge = 'qbr%s' % iface_id
        ovs_bridge = vif['network']['bridge']

        try:
            if not linux_net.device_exists(if_bridge):
                utils.execute('brctl', 'addbr', if_bridge, run_as_root=True)
                utils.execute('brctl', 'setfd', if_bridge, 0, run_as_root=True)
                utils.execute('brctl', 'stp', if_bridge, 'off', run_as_root=True)
                utils.execute('tee',
                              ('/sys/class/net/%s/bridge/multicast_snooping' %
                               if_bridge),
                              process_input='0',
                              run_as_root=True,
                              check_exit_code=[0, 1])


            if not linux_net.device_exists(v2_name):
                linux_net._create_veth_pair(v1_name, v2_name)
                utils.execute('ip', 'link', 'set', if_bridge, 'up', run_as_root=True)
                utils.execute('brctl', 'addif', if_bridge, v1_name, run_as_root=True)
                linux_net.create_ovs_vif_port(ovs_bridge,
                                              v2_name, vif['id'], vif['address'],
                                              instance['uuid'])

            if not linux_net.device_exists(if_local_name):
                utils.execute('ip', 'link', 'add', 'name', if_local_name, 'type',
                              'veth', 'peer', 'name', if_remote_name,
                              run_as_root=True)
                utils.execute('ip', 'link', 'set', if_local_name, 'up',
                              run_as_root=True)
                utils.execute('brctl', 'addif', if_bridge, if_local_name,
                              run_as_root=True)
        except Exception:
            LOG.exception("Failed to configure network in hybird type.")
            msg = _('Failed to setup the network, rolling back')
            undo_mgr.rollback_and_reraise(msg=msg, instance=instance)

    # We are creating our own mac's now because the linux bridge interface
    # takes on the lowest mac that is assigned to it.  By using FE range
    # mac's we prevent the interruption and possible loss of networking
    # from changing mac addresses.
    def _fe_random_mac(self):
        mac = [0xfe, 0xed,
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]
        return ':'.join(map(lambda x: "%02x" % x, mac))

    def plug_bridge(self, instance, vif):
        if_local_name = 'tap%s' % vif['id'][:11]
        if_remote_name = 'ns%s' % vif['id'][:11]
        bridge = vif['network']['bridge']
        gateway = network.find_gateway(instance, vif['network'])

        vlan = vif.get('vlan')
        if vlan is not None:
            iface = (CONF.vlan_interface or
                     vif['network']['meta']['bridge_interface'])
            linux_net.LinuxBridgeInterfaceDriver.ensure_vlan_bridge(
                vlan,
                bridge,
                iface,
                net_attrs=vif,
                mtu=vif.get('mtu'))
            iface = 'vlan%s' % vlan
        else:

            iface = (CONF.flat_interface or
                     vif['network']['meta']['bridge_interface'])
            LOG.debug('Ensuring bridge for %s - %s' % (iface, bridge))
            linux_net.LinuxBridgeInterfaceDriver.ensure_bridge(
                bridge,
                iface,
                net_attrs=vif,
                gateway=gateway)

        # Device already exists so return.
        if linux_net.device_exists(if_local_name):
            return
        undo_mgr = utils.UndoManager()

        try:
            utils.execute('ip', 'link', 'add', 'name', if_local_name, 'type',
                          'veth', 'peer', 'name', if_remote_name,
                          run_as_root=True)
            undo_mgr.undo_with(lambda: utils.execute(
                'ip', 'link', 'delete', if_local_name, run_as_root=True))
            # NOTE(samalba): Deleting the interface will delete all
            # associated resources (remove from the bridge, its pair, etc...)
            utils.execute('ip', 'link', 'set', if_local_name, 'address',
                          self._fe_random_mac(), run_as_root=True)
            utils.execute('brctl', 'addif', bridge, if_local_name,
                          run_as_root=True)
            utils.execute('ip', 'link', 'set', if_local_name, 'up',
                          run_as_root=True)
        except Exception:
            LOG.exception("Failed to configure network")
            msg = _('Failed to setup the network, rolling back')
            undo_mgr.rollback_and_reraise(msg=msg, instance=instance)

    def unplug(self, instance, vif):
        vif_type = vif['type']

        LOG.debug('vif_type=%(vif_type)s instance=%(instance)s '
                  'vif=%(vif)s',
                  {'vif_type': vif_type, 'instance': instance,
                   'vif': vif})

        if vif_type is None:
            raise exception.NovaException(
                _("vif_type parameter must be present "
                  "for this vif_driver implementation"))

        if vif_type == network_model.VIF_TYPE_BRIDGE:
            self.unplug_bridge(instance, vif)
        elif vif_type == network_model.VIF_TYPE_OVS:
            self.unplug_ovs(instance, vif)
        else:
            raise exception.NovaException(
                _("Unexpected vif_type=%s") % vif_type)

    def unplug_ovs(self, instance, vif):
        if CONF.docker.ovs_work_type == "hybird" and  vif.is_hybrid_plug_enabled():
            LOG.debug('ovs type is hybird..')
            self.unplug_ovs_hybird(instance, vif)
        else:
            LOG.debug('ovs type is direct')
            self.unplug_ovs_bridge(instance, vif)

    def unplug_ovs_hybird(self, instance, vif):
        """Unplug the VIF by deleting the port from the ovs hybird ovs mode."""
        iface_id = vif['id'][:11]
        if_local_name = 'tap%s' % iface_id
        v1_name = 'qvb%s' % iface_id
        v2_name = 'qvo%s' % iface_id
        if_bridge = 'qbr%s' % iface_id
        ovs_bridge = vif['network']['bridge']
        try:
            #del linux br
            if linux_net.device_exists(if_bridge):
                utils.execute('brctl', 'delif', if_bridge, v1_name, run_as_root=True)
                utils.execute('ip', 'link', 'set', if_bridge, 'down', run_as_root=True)
                utils.execute('brctl', 'delbr', if_bridge, run_as_root=True)
            #del tap veth pair
            if linux_net.device_exists(if_local_name):
                utils.execute('ip', 'link', 'delete', if_local_name, run_as_root=True)
           #del qvb veth pair
            if linux_net.device_exists(v1_name):
                utils.execute('ip', 'link', 'delete', v1_name, run_as_root=True)
            #ip link delete pair1
            linux_net.delete_ovs_vif_port(ovs_bridge,v2_name)
        except processutils.ProcessExecutionError:
            LOG.exception(_("Failed while unplugging vif"), instance=instance)

    def unplug_ovs_bridge(self, instance, vif):
        """Unplug the VIF by deleting the port from the bridge."""
        try:
            linux_net.delete_ovs_vif_port(vif['network']['bridge'],
                                          vif['devname'])
        except processutils.ProcessExecutionError:
            LOG.exception(_("Failed while unplugging vif"), instance=instance)

    def unplug_bridge(self, instance, vif):
        # NOTE(arosen): nothing has to be done in the linuxbridge case
        # as when the veth is deleted it automatically is removed from
        # the bridge.
        pass

    def attach(self, instance, vif, container_id, sec_if=False):
        vif_type = vif['type']
        if_remote_name = 'ns%s' % vif['id'][:11]
        if not sec_if:
            if_remote_rename = 'eth0'
        else:
            if_remote_rename = 'eth1'
        gateway = network.find_gateway(instance, vif['network'])
        ip = network.find_fixed_ip(instance, vif['network'])
        ip_nocidr = ip.split('/')[0]
        dhcp_server = network.find_dhcp_server(instance, vif['network'])

        LOG.debug('attach vif_type=%(vif_type)s instance=%(instance)s '
                  'vif=%(vif)s',
                  {'vif_type': vif_type, 'instance': instance,
                   'vif': vif})

        try:
            utils.execute('ip', 'link', 'set', if_remote_name, 'netns',
                          container_id, run_as_root=True)
            utils.execute('ip', 'netns', 'exec', container_id, 'ip', 'link',
                          'set', if_remote_name, 'name', if_remote_rename,
                          run_as_root=True)
            utils.execute('ip', 'netns', 'exec', container_id, 'ip', 'link',
                          'set', if_remote_rename, 'address', vif['address'],
                          run_as_root=True)
            utils.execute('ip', 'netns', 'exec', container_id, 'ifconfig',
                          if_remote_rename, ip, run_as_root=True)
            utils.execute('ip', 'netns', 'exec', container_id, 'ip', 'link',
                          'set', if_remote_rename, 'up', run_as_root=True)


            if not sec_if:
                utils.execute('ip', 'netns', 'exec', container_id,
                              'ip', 'route', 'replace', 'default', 'via',
                              gateway, 'dev', if_remote_rename, run_as_root=True)
                if dhcp_server:
                    utils.execute('ip', 'netns', 'exec', container_id, 'ip', 'route', 'add',
                                  '169.254.169.254/32', 'via', dhcp_server)
                else:
                    LOG.warning("Cloudinit Cloud not work for %s, no dhcp_server info "
                                "in network meta." % container_id)


            # Disable TSO, for now no config option
            #utils.execute('ip', 'netns', 'exec', container_id, 'ethtool',
            #              '--offload', if_remote_rename, 'tso', 'off',
            #              run_as_root=True)

            #send free arp avovid apr proxy in switch.
            utils.execute('ip', 'netns', 'exec', container_id,
                          'arping', '-c', '1' ,'-U', '-I',
                          if_remote_rename, ip_nocidr, run_as_root=True)
            #Error while ping the gateway, put an init script in docker_init_exc.
            #utils.execute('ip', 'netns', 'exec', container_id,
            #             'ping', '-c', '1' ,
            #            gateway, run_as_root=True)
        except Exception:
            LOG.exception("Failed to attach vif")
