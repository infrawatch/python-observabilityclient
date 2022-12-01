General information
-------------------

**observabilityclient** is an OpenStackClient (OSC) plugin implementation that
implements commands for management of OpenStack observability components
such as Prometheus, collectd and Ceilometer.

How to use
----------
Run the following as the stack user on your undercloud
::

  mkdir obsclient
  cd obsclient/
  git clone https://github.com/infrawatch/python-observabilityclient.git
  git clone https://github.com/infrawatch/osp-observability-ansible.git
  cd python-observabilityclient/
  sudo python3 setup.py install --prefix=/usr
  cd ../osp-observability-ansible/
  sudo mkdir /usr/share/osp-observability
  sudo chmod a+rx /usr/share/osp-observability
  sudo ln -s /home/stack/obsclient/osp-observability-ansible/playbooks /usr/share/osp-observability/playbooks
  sudo chmod a+rx /usr/share/osp-observability/playbooks
  sudo ln -s /home/stack/obsclient/osp-observability-ansible/roles/spawn_container /usr/share/ansible/roles/spawn_container
  sudo ln -s /home/stack/obsclient/osp-observability-ansible/roles/osp_observability /usr/share/ansible/roles/osp_observability
  sudo mkdir /var/lib/osp-observability
  sudo chmod a+rwx /var/lib/osp-observability
  cd
  source stackrc
  openstack observability discover
  echo "prometheus_remote_write: ['http://someurl', 'http://otherurl']" > test_params.yaml
  openstack observability setup prometheus_agent --config ./test_params.yaml
