__author__ = 'Danylo Bilyk'

from .request import Request
from pt.protocol import ProtocolMessage
from pt.worker import Worker
from pt.processors import WorkerInfo
from pt.utils import logger


class RestartRequest(Request):
    __metaclass__ = ProtocolMessage

    _FIELDS = {
        'reason': None,
        'target': '*'
    }

    def __init__(self, *args, **kwargs):
        super(RestartRequest, self).__init__(*args, **kwargs)

    def perform(self):
        self_info = WorkerInfo.own()
        if str(self.target) in (self_info.name, self_info.ip) or str(self.target) == '*':
            logger.warn('Restarting worker process by reason [%s]' % self.reason)
            Worker().restart()
