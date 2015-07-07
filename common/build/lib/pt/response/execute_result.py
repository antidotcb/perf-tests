__author__ = 'Danylo Bilyk'

from pt.protocol.response import Response

from pt.protocol import ProtocolMessage


class ScriptResult(Response):
    __metaclass__ = ProtocolMessage

    _DEFAULTS = {
        'result': 0,
        'output': ''
    }

    def __init__(self, *args, **kwargs):
        super(ScriptResult, self).__init__(*args, **kwargs)

    def collect(self):
        super(ScriptResult, self).collect()
