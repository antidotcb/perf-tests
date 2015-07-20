__author__ = 'Danylo Bilyk'

from pt.protocol import JsonMessage
from pt.utils import WorkerInfo


class Response(JsonMessage):
    _DEFAULTS = {
        'client': WorkerInfo.own().name,
        'group': WorkerInfo.own().group,
        'ip': WorkerInfo.own().ip
    }

    def __init__(self, *args, **kwargs):
        super(Response, self).__init__(*args, **kwargs)
