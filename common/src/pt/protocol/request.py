__author__ = 'Danylo Bilyk'

from uuid import uuid4

from pt.protocol import JsonMessage
from pt.utils import WorkerInfo


class Request(JsonMessage):
    _DEFAULTS = {
        'uuid': uuid4,
        'target': '*'
    }

    def __init__(self, *args, **kwargs):
        super(Request, self).__init__(*args, **kwargs)

    def _is_target(self):
        own = WorkerInfo.own()
        return str(self.target) in (own.name, own.ip) or str(self.target) == '*'

    def perform(self):
        raise NotImplemented()
