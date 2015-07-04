__author__ = 'Danylo Bilyk'

from pt.protocol import JsonMessage


class Response(JsonMessage):
    def __init__(self, *args, **kwargs):
        super(Response, self).__init__(*args, **kwargs)

    def collect(self):
        raise NotImplemented()
