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

## Usage

Use `openstack observabilityclient query somequery` to query for metrics in prometheus.

To use the python api do the following:
```
from observabilityclient import client

c = client.Client(
            '1', keystone_client.get_session(conf),
            adapter_options={
                'interface': conf.service_credentials.interface,
                'region_name': conf.service_credentials.region_name})
c.query.query("somequery")
```
