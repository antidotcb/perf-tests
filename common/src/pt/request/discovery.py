__author__ = 'Danylo Bilyk'

from pt.protocol.request import Request
from pt.protocol import protocol, ProtocolMessage
from pt.response import DiscoveryResponse
from pt.utils import log


class DiscoveryRequest(Request):
    __metaclass__ = ProtocolMessage

    _DEFAULTS = {
        'message': 'Default message',
        'response': protocol.typename(DiscoveryResponse)
    }

    def __init__(self, *args, **kwargs):
        super(DiscoveryRequest, self).__init__(*args, **kwargs)

    def perform(self):
        log.debug('Just creating response with own id: %s', self.uuid)
        return protocol.construct(self.response, request_uuid=self.uuid)
