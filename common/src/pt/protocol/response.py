__author__ = 'Danylo Bilyk'

from pt.protocol import JsonMessage
from pt.utils import WorkerInfo


class Response(JsonMessage):
    def __init__(self, *args, **kwargs):
        self.name = WorkerInfo().own().name
        self.group = WorkerInfo().own().group
        self.ip = WorkerInfo().own().ip
        self.uuid = WorkerInfo().own().uuid
        super(Response, self).__init__(*args, **kwargs)

