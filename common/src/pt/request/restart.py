__author__ = 'Danylo Bilyk'

from pt.protocol import Request
from pt.protocol import ProtocolMessage


class RestartRequest(Request):
    __metaclass__ = ProtocolMessage

    _DEFAULTS = {
        'reason': None,
    }

    def __init__(self, *args, **kwargs):
        super(RestartRequest, self).__init__(*args, **kwargs)
