# python-observabilityclient

observabilityclient is an OpenStackClient (OSC) plugin implementation that
implements commands for management of Prometheus.

## Development

Install your OpenStack environment and patch your `openstack` client application using python.

```
# if using standalone, the following commands come after 'sudo dnf install -y python3-tripleoclient'

su - stack

# clone and install observability client plugin
git clone https://github.com/infrawatch/python-observabilityclient
cd python-observabilityclient
sudo python setup.py install --prefix=/usr
```
