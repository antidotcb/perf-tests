__author__ = 'Danylo Bilyk'

from pt.protocol import JsonMessage
from pt.utils import WorkerInfo, logger


class Response(JsonMessage):
    _DEFAULTS = {
        'client': WorkerInfo.own().name,
        'ip': WorkerInfo.own().ip
    }

    def __init__(self, *args, **kwargs):
        super(Response, self).__init__(*args, **kwargs)

    def collect(self):
        logger.info('Collected response: %s', self.to_json())
