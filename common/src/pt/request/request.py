__author__ = 'Danylo Bilyk'

from pt.protocol import Message


class Request(Message):
    def __init__(self, *args, **kwargs):
        super(Request, self).__init__(*args, **kwargs)

    def perform(self):
        raise NotImplemented()
