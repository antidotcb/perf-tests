__author__ = 'Danylo Bilyk'

from pt.protocol import JsonMessage
from pt.response import DiscoveryResponse


class DiscoveryRequest(JsonMessage):
    _FIELDS = {
        'message': 'Default message',
        'response': DiscoveryResponse.__class__.__name__
    }

    def __init__(self, *args, **kwargs):
        super(DiscoveryRequest, self).__init__(*args, **kwargs)
        pass
