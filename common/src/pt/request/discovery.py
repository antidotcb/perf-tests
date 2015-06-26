__author__ = 'Danylo Bilyk'

from pt.protocol import Census
from pt.protocol import JsonMessage
from pt.response import DiscoveryResponse

class DiscoveryRequest(JsonMessage):
    _FIELDS = {
        'message': 'Default message',
        'response': Census().typename(DiscoveryResponse)
    }

    def __init__(self, *args, **kwargs):
        super(DiscoveryRequest, self).__init__(*args, **kwargs)
        self._census = Census()

    def perform(self):
        return self._census.construct(self.response)
