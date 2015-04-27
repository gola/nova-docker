#dockerbase:v7
#docker build -t="dockerbase:v7" .
#docker save dockerbase > dockerbase-v7.tar
#glance image-create --is-public=True --container-format=docker --disk-format=raw --name dockerbase:v7 < dockerbase-v7.tar
From rhel:6.3

# config ssh 
RUN mkdir -p /root/.ssh && chown root.root /root && chmod 700 /root/.ssh && touch /root/.ssh/authorized_keys && chmod 600 /root/.ssh/authorized_keys
ADD ssh /root/.ssh/
RUN cat /root/.ssh/suning_keys >> /root/.ssh/authorized_keys && rm -f /root/.ssh/suning_keys
RUN echo 'root:cloud@123' | chpasswd
RUN sed  -i "/^[^#]*UsePAM/ s/.*/#&/"  /etc/ssh/sshd_config
RUN echo "UsePAM no" >> /etc/ssh/sshd_config
RUN sed  -i "/^[^#]*UseDNS/ s/.*/#&/"  /etc/ssh/sshd_config
RUN echo "UseDNS no" >> /etc/ssh/sshd_config
RUN echo "ClientAliveInterval 600" >> /etc/ssh/sshd_config
RUN echo "ClientAliveCountMax 0" >> /etc/ssh/sshd_config
RUN echo "UseLogin yes" >> /etc/ssh/sshd_config
RUN ssh-keygen -q -N "" -t dsa -f /etc/ssh/ssh_host_dsa_key
RUN ssh-keygen -q -N "" -t rsa -f /etc/ssh/ssh_host_rsa_key

#system safe config
RUN sed -i 's/PASS_MAX_DAYS.*/PASS_MAX_DAYS  180/' /etc/login.defs
RUN sed -i 's/PASS_MIN_LEN.*/PASS_MIN_LEN  8/' /etc/login.defs
RUN sed -i 's/HISTSIZE=1000/HISTSIZE=100/' /etc/profile

#add
ADD yum.repos.d /etc/yum.repos.d
ADD supervisord.conf /etc/supervisord.conf

# install salt-minion in repo http://192.168.86.5/rh63/x86_64/Salt/2014.1.4/ and Required packages in http://192.168.86.5/rh63/x86_64/Salt/0.17.2/salt-Requires/
RUN yum install -y python-crypto python-babel pciutils libyaml yum-utils libyaml zeromq3 python-jinja2 python-msgpack PyYAML salt-minion python-zmq salt sshpass wget tar perl unzip
RUN yum update -y bash openssl glibc
# fix passwd command err: /usr/share/cracklib/pw_dict.pwd: No such file or directory 
RUN yum reinstall -y cracklib-dicts

#install supervisor
ADD RPM /tmp/
RUN rpm -ivh /tmp/supervisor-2.1-8.el6.noarch.rpm /tmp/python-meld3-0.6.7-1.el6.x86_64.rpm 
RUN rm -rf /tmp/*

#HEHE,I can only say this. the host department let me do this.
RUN adduser snadmin

#init script and command.
RUN mkdir -p /var/log/supervisor
RUN mkdir -p /etc/openstack-docker
ADD startup.sh /bin/startup.sh
CMD /bin/startup.sh && sysctl -p && supervisord
