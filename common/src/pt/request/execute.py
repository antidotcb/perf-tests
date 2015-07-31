__author__ = 'Danylo Bilyk'

from pt.protocol import Request
from pt.protocol import ProtocolMessage
from pt.response import ExecuteResponse


class ExecuteRequest(Request):
    __metaclass__ = ProtocolMessage

    _TIMEOUT = 10  # seconds
    _RESPONSE = ExecuteResponse

    def __init__(self, *args, **kwargs):
        self.script = None
        self.cwd = None
        self.timeout = ExecuteRequest._TIMEOUT
        super(ExecuteRequest, self).__init__(*args, **kwargs)

    def request_timeout(self):
        return self.timeout
