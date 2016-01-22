# Copyright (c) 2014 Docker, Inc.
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


from nova import utils
from nova.openstack.common import processutils


def sys_uptime():
    """Returns the result of calling "uptime"."""
    out, err = utils.execute('env', 'LANG=C', 'uptime')
    return out

def execute(*args, **kwargs):
    return utils.execute(*args, **kwargs)

def copy_image(src, dest, host=None):
    """Copy a disk image to an existing directory

    :param src: Source image
    :param dest: Destination path
    :param host: Remote host
    """
    if not host:
        # We shell out to cp because that will intelligently copy
        # sparse files.  I.E. holes will not be written to DEST,
        # rather recreated efficiently.  In addition, since
        # coreutils 8.11, holes can be read efficiently too.
        execute('cp', src, dest)
    else:
        dest = "%s:%s" % (host, dest)
        # Try rsync first as that can compress and create sparse dest files.
        # Note however that rsync currently doesn't read sparse files
        # efficiently: https://bugzilla.samba.org/show_bug.cgi?id=8918
        # At least network traffic is mitigated with compression.
        try:
            # Do a relatively light weight test first, so that we
            # can fall back to scp, without having run out of space
            # on the destination for example.
            execute('rsync', '-apur', src, dest)
        except processutils.ProcessExecutionError:
            execute('scp', '-r', src, dest)
