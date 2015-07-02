__author__ = 'Danylo Bilyk'

from pt.request import Request
from pt.protocol import MessageCatalog
from pt.protocol import RegisteredMessage
from pt.response import DiscoveryResponse


class DiscoveryRequest(Request):
    __metaclass__ = RegisteredMessage

    _FIELDS = {
        'message': 'Default message',
        'response': MessageCatalog().typename(DiscoveryResponse)
    }

    def __init__(self, *args, **kwargs):
        super(DiscoveryRequest, self).__init__(*args, **kwargs)
        self._catalog = MessageCatalog()

    def perform(self):
        return self._catalog.construct(self.response)
