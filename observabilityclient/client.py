import sys
def Client(version, *args, **kwargs):
    module = 'observabilityclient.v%s.client' % version
    __import__(module)
    client_class = getattr(sys.modules[module], 'Client')
    return client_class(*args, **kwargs)


