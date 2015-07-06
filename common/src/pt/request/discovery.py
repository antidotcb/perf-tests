__author__ = 'Danylo Bilyk'

from pt.protocol.request import Request
from pt.protocol import Protocol, ProtocolMessage
from pt.response import DiscoveryResponse
from pt.utils import logger


class DiscoveryRequest(Request):
    __metaclass__ = ProtocolMessage

    _DEFAULTS = {
        'message': 'Default message',
        'response': Protocol().typename(DiscoveryResponse)
    }

    def __init__(self, *args, **kwargs):
        super(DiscoveryRequest, self).__init__(*args, **kwargs)
        self._catalog = Protocol()

    def perform(self):
        logger.debug('Just creating response with own id: %s', self.uuid)
        return self._catalog.construct(self.response, request_uuid=self.uuid)
