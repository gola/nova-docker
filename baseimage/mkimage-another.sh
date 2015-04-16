#!/bin/bash
 
if [ $UID -ne 0 ]; then
  echo "You need to run this script as root"
  exit 1
fi
 
NAME=wildfly-minimal
BUILDDIR=`pwd`/build
 
# Removing the earlier build
rm -rf $BUILDDIR
 
# Install the required stuff
yum -y install wildfly \
  --setopt=override_install_langs=en \
  --setopt=tsflags=nodocs \
  --installroot $BUILDDIR \
  --disablerepo=* \
  --enablerepo=fedora,updates,updates-testing \
  --releasever=20 \
  --nogpgcheck
 
# Clean up the cache
# and fix the console issue when running the image
chroot $BUILDDIR /bin/bash -x <<EOF
rm -rf /var/cache/yum/*
rm -rf /dev/console
ln -s /dev/tty1 /dev/console
EOF
 
# Import to Docker
tar -C $BUILDDIR -c . | docker import - $NAME

