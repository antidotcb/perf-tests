__author__ = 'Danylo Bilyk'

from uuid import uuid4
from pt.protocol import JsonMessage, protocol


class Request(JsonMessage):
    _DEFAULTS = {
        'target': '*',
        'response': None
    }

    def __init__(self, *args, **kwargs):
        super(Request, self).__init__(*args, **kwargs)
        self._properties.correlation_id = uuid4()

    def properties(self):
        return self._properties

    def perform(self):
        return protocol.construct(self.response)
