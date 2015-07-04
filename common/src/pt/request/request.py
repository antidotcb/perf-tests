__author__ = 'Danylo Bilyk'

from pt.protocol import JsonMessage


class Request(JsonMessage):
    def __init__(self, *args, **kwargs):
        super(Request, self).__init__(*args, **kwargs)

    def perform(self):
        raise NotImplemented()
