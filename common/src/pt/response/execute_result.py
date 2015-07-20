__author__ = 'Danylo Bilyk'

from pt.protocol import Response

from pt.protocol import ProtocolMessage


class ExecuteResult(Response):
    __metaclass__ = ProtocolMessage

    _DEFAULTS = {
        'output': '',
        'result': 0
    }

    def __init__(self, *args, **kwargs):
        super(ExecuteResult, self).__init__(*args, **kwargs)
