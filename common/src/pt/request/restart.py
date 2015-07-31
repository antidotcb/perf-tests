__author__ = 'Danylo Bilyk'

from pt.protocol import Request
from pt.protocol import ProtocolMessage


class RestartRequest(Request):
    __metaclass__ = ProtocolMessage

    _TIMEOUT = 0  # seconds

    def __init__(self, *args, **kwargs):
        self.reason = None
        super(RestartRequest, self).__init__(*args, **kwargs)
