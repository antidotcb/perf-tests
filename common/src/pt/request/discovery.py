__author__ = 'Danylo Bilyk'

from pt.protocol import Request
from pt.protocol import ProtocolMessage
from pt.response import DiscoveryResponse


class DiscoveryRequest(Request):
    __metaclass__ = ProtocolMessage

    _TIMEOUT = 2  # seconds
    _RESPONSE = DiscoveryResponse

    def __init__(self, *args, **kwargs):
        super(DiscoveryRequest, self).__init__(*args, **kwargs)
