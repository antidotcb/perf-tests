__author__ = 'Danylo Bilyk'

from pt.protocol import Response

from pt.protocol import ProtocolMessage


class ExecuteResponse(Response):
    __metaclass__ = ProtocolMessage

    def __init__(self, *args, **kwargs):
        self.output = None
        self.result = None
        super(ExecuteResponse, self).__init__(*args, **kwargs)
