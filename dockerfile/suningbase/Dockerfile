#dockerbase:v5
#docker build -t="dockerbase:v5" .
#docker save dockerbase > dockerbase-v5.tar
#glance image-create --is-public=True --container-format=docker --disk-format=raw --name dockerbase:v5 < dockerbase-v5.tar
From rhel:6.3

# config ssh 
RUN mkdir -p /root/.ssh && chown root.root /root && chmod 700 /root/.ssh
RUN echo 'root:cloud@123' | chpasswd
RUN sed  -i "/^[^#]*UsePAM/ s/.*/#&/"  /etc/ssh/sshd_config
RUN echo "UsePAM no" >> /etc/ssh/sshd_config
RUN sed  -i "/^[^#]*UseDNS/ s/.*/#&/"  /etc/ssh/sshd_config
RUN echo "UseDNS no" >> /etc/ssh/sshd_config
RUN ssh-keygen -q -N "" -t dsa -f /etc/ssh/ssh_host_dsa_key
RUN ssh-keygen -q -N "" -t rsa -f /etc/ssh/ssh_host_rsa_key

#add
ADD yum.repos.d /etc/yum.repos.d
ADD RPM /tmp/
ADD supervisord.conf /etc/supervisord.conf

# install salt-minion in repo http://192.168.86.5/rh63/x86_64/Salt/2014.1.4/ and Required packages in http://192.168.86.5/rh63/x86_64/Salt/0.17.2/salt-Requires/
RUN yum install -y python-crypto python-babel pciutils libyaml yum-utils libyaml zeromq3
RUN rpm -ivh /tmp/python-jinja2-2.2.1-1.el6.x86_64.rpm /tmp/python-msgpack-0.1.13-3.el6.x86_64.rpm /tmp/PyYAML-3.10-3.el6.x86_64.rpm  /tmp/salt-minion-2014.1.4-1.el6.noarch.rpm /tmp/python-zmq-2.2.0.1-1.el6.x86_64.rpm /tmp/salt-2014.1.4-1.el6.noarch.rpm /tmp/sshpass-1.05-5.el6.art.x86_64.rpm

#HEHE,I can only say this. the host department let me do this.
RUN yum install -y wget tar perl unzip
RUN yum update -y bash openssl
RUN adduser snadmin

#install supervisor
RUN mkdir -p /var/log/supervisor
RUN rpm -ivh /tmp/supervisor-2.1-8.el6.noarch.rpm /tmp/python-meld3-0.6.7-1.el6.x86_64.rpm

# fix passwd command err: /usr/share/cracklib/pw_dict.pwd: No such file or directory 
RUN yum reinstall -y cracklib-dicts

# clean tmp data.
RUN rm -rf /tmp/*

#init script and command.
RUN mkdir -p /etc/openstack-docker
ADD startup.sh /bin/startup.sh
CMD /bin/startup.sh && sysctl -p && supervisord
