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

import functools
import inspect
import six
from nova.openstack.common import log as logging
from oslo.config import cfg
from docker import client
from docker import tls

CONF = cfg.CONF
DEFAULT_TIMEOUT_SECONDS = 120
DEFAULT_DOCKER_API_VERSION = '1.17'
LOG = logging.getLogger(__name__)


def filter_data(f):
    """Decorator that post-processes data returned by Docker.
     This will avoid any surprises with different versions of Docker.
    """
    @functools.wraps(f, assigned=[])
    def wrapper(*args, **kwds):
        out = f(*args, **kwds)

        def _filter(obj):
            if isinstance(obj, list):
                new_list = []
                for o in obj:
                    new_list.append(_filter(o))
                obj = new_list
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(k, six.string_types):
                        obj[k.lower()] = _filter(v)
            return obj
        return _filter(out)
    return wrapper

class DockerHTTPClient(client.Client):
    def __init__(self, url='unix://var/run/docker.sock'):
        ssl_config = False
        #__init__(self, base_url=None, version=None, timeout=60, tls=False)
        super(DockerHTTPClient, self).__init__(
            base_url=url,
            version=DEFAULT_DOCKER_API_VERSION,
            timeout=DEFAULT_TIMEOUT_SECONDS,
            tls=ssl_config
        )
        self._setup_decorators()

    def _setup_decorators(self):
        for name, member in inspect.getmembers(self, inspect.ismethod):
            if not name.startswith('_'):
                setattr(self, name, filter_data(member))

    def create_container(self, args, name):
        data = {
            'Hostname': '',
            'User': '',
            'Memory': 0,
            'MemorySwap': 0,
            'AttachStdin': False,
            'AttachStdout': False,
            'AttachStderr': False,
            'PortSpecs': [],
            'Tty': True,
            'OpenStdin': True,
            'StdinOnce': False,
            'Env': None,
            'Cmd': [],
            'Dns': None,
            'Image': None,
            'Volumes': {},
            'VolumesFrom': '',
            'HostConfig': {
                "Privileged": True,
            }
        }
        data.update(args)
        resp = self.make_request(
            'POST',
            'containers/create',
            ('name', unicode(name).encode('utf-8')),
            body=jsonutils.dumps(data))
        if resp.code != 201:
            return
        obj = resp.to_json()
        for k, v in obj.iteritems():
            if k.lower() == 'id':
                return v

    def start_container(self, container_id):
        resp = self.make_request(
            'POST',
            'containers/{0}/start'.format(container_id),
            body='{}')
        return (resp.code == 200 or resp.code == 204)

    def pause_container(self, container_id):
        resp = self.make_request(
            'POST',
            'containers/{0}/pause'.format(container_id),
            body='{}')
        return (resp.code == 204)

    def unpause_container(self, container_id):
        resp = self.make_request(
            'POST',
            'containers/{0}/unpause'.format(container_id),
            body='{}')
        return (resp.code == 204)

    def inspect_image(self, image_name):
        resp = self.make_request(
            'GET',
            'images/{0}/json'.format(
                unicode(image_name).encode('utf-8')))
        if resp.code != 200:
            return
        return resp.to_json()

    def stop_container(self, container_id, timeout=5):
        resp = self.make_request(
            'POST',
            'containers/{0}/stop'.format(container_id),
            ('t', timeout))
        return (resp.code == 204)

    def kill_container(self, container_id):
        resp = self.make_request(
            'POST',
            'containers/{0}/kill'.format(container_id))
        return (resp.code == 204)

    def destroy_container(self, container_id):
        resp = self.make_request(
            'DELETE',
            'containers/{0}'.format(container_id))
        return (resp.code == 204)

    def get_image(self, name, size=4096):
        parts = unicode(name).encode('utf-8').rsplit(':', 1)
        url = 'images/{0}/get'.format(parts[0])
        resp = self.make_request('GET', url)

        while True:
            buf = resp.read(size)
            if not buf:
                break
            yield buf
        return

    def get_image_resp(self, name):
        parts = unicode(name).encode('utf-8').rsplit(':', 1)
        url = 'images/{0}/get'.format(parts[0])
        resp = self.make_request('GET', url)
        return resp

    def load_repository(self, name, data):
        url = 'images/load'
        self.make_request('POST', url, body=data)

    def load_repository_file(self, name, path):
        with open(path) as fh:
            self.load_repository(unicode(name).encode('utf-8'), fh)

    def commit_container(self, container_id, name):
        parts = unicode(name).encode('utf-8').rsplit(':', 1)
        url = 'commit'
        query = [('container', container_id),
                 ('repo', parts[0])]

        if len(parts) > 1:
            query += (('tag', parts[1]),)
        resp = self.make_request('POST', url, *query)
        return (resp.code == 201)

    def get_container_logs(self, container_id):
        resp = self.make_request(
            'POST',
            'containers/{0}/attach'.format(container_id),
            ('logs', '1'),
            ('stream', '0'),
            ('stdout', '1'),
            ('stderr', '1'))
        if resp.code != 200:
            return
        return resp.read()

    #Add by Mars Gu - 2014-10-21.
    def tag(self,image_id,image_name):
        default_tag = (':' not in image_name)
        image_name = image_name if not default_tag else image_name + ':latest'
        resp = self.make_request(
            'POST',
            'images/{0}/tag'.format(image_id),
            ('repo', image_name.split(":")[0]),
            ('force', '0'),
            ('tag', image_name.split(":")[1]))
        return (resp.code == 201)

    #Add by Mars Gu - 2015-06-02
    def docker_daemon_info(self):
        resp = self.make_request('GET', 'info')
        if resp.code != 200:
            return {}
        return resp.to_json()
