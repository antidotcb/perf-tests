__author__ = 'Danylo Bilyk'

from pt.protocol import JsonMessage


class Request(JsonMessage):
    _DEFAULTS = {}

    def __init__(self, *args, **kwargs):
        super(Request, self).__init__(*args, **kwargs)
