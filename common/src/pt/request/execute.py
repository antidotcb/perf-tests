__author__ = 'Danylo Bilyk'

from pt.protocol import Request
from pt.protocol import ProtocolMessage


class ExecuteRequest(Request):
    __metaclass__ = ProtocolMessage

    def __init__(self, *args, **kwargs):
        self.script = None
        self.cwd = None
        self.timeout = 60
        super(ExecuteRequest, self).__init__(*args, **kwargs)
