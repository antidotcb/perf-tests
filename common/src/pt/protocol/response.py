__author__ = 'Danylo Bilyk'

from pt.protocol import JsonMessage
from pt.utils import config


class Response(JsonMessage):
    def __init__(self, *args, **kwargs):
        self.name = config.name()
        self.group = config.group()
        self.ip = config.ip()
        self.uuid = config.uuid()
        super(Response, self).__init__(*args, **kwargs)
