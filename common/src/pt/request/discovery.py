__author__ = 'Danylo Bilyk'

from pt.protocol import Request
from pt.protocol import protocol, ProtocolMessage
from pt.response import DiscoveryResponse


class DiscoveryRequest(Request):
    __metaclass__ = ProtocolMessage

    _DEFAULTS = {
        'response': protocol.typename(DiscoveryResponse)
    }

    def __init__(self, *args, **kwargs):
        super(DiscoveryRequest, self).__init__(*args, **kwargs)
