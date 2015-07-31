__author__ = 'Danylo Bilyk'

from pt.protocol import JsonMessage


class Request(JsonMessage):
    _TIMEOUT = 10
    _RESPONSE = None

    def __init__(self, *args, **kwargs):
        super(Request, self).__init__(*args, **kwargs)

    def request_timeout(self):
        return self.__class__._TIMEOUT

    def response_type(self):
        return self.__class__._RESPONSE
