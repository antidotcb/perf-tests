__author__ = 'Danylo Bilyk'

from pt.protocol import Request, ProtocolMessage


class TerminateRequest(Request):
    __metaclass__ = ProtocolMessage

    _TIMEOUT = 0  # seconds

    def __init__(self, *args, **kwargs):
        self.reason = None
        super(TerminateRequest, self).__init__(*args, **kwargs)
