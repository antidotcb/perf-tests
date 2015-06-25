__author__ = 'Danylo Bilyk'

from pt.utils import JsonMessage
# from pt import Config

def client_id():
    name = Config().name
    return name


class DiscoveryResponse(JsonMessage):
    _FIELDS = {
        'client': client_id
    }

    def __init__(self, *args, **kwargs):
        super(DiscoveryResponse, self).__init__(*args, **kwargs)
        pass