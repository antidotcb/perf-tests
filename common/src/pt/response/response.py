__author__ = 'Danylo Bilyk'

from pt.protocol import Message


class Response(Message):
    def __init__(self, *args, **kwargs):
        super(Response, self).__init__(*args, **kwargs)

    def collect(self):
        raise NotImplemented()
