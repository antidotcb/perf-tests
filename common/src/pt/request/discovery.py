__author__ = 'Danylo Bilyk'

from pt.request import Request
from pt.protocol import Protocol, ProtocolMessage
from pt.response import DiscoveryResponse


class DiscoveryRequest(Request):
    __metaclass__ = ProtocolMessage

    _FIELDS = {
        'message': 'Default message',
        'response': Protocol().typename(DiscoveryResponse)
    }

    def __init__(self, *args, **kwargs):
        super(DiscoveryRequest, self).__init__(*args, **kwargs)
        self._catalog = Protocol()

    def perform(self):
        return self._catalog.construct(self.response)
