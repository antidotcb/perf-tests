__author__ = 'Danylo Bilyk'

from pt.protocol import Response

from pt.protocol import ProtocolMessage


class DiscoveryResponse(Response):
    __metaclass__ = ProtocolMessage

    _DEFAULTS = {}

    def __init__(self, *args, **kwargs):
        super(DiscoveryResponse, self).__init__(*args, **kwargs)
