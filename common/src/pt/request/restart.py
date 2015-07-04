__author__ = 'Danylo Bilyk'

from .request import Request
from pt.worker import Worker
from pt.utils import logger


class RestartRequest(Request):
    _FIELDS = {
        'reason': None,
        'target': '*'
    }

    def __init__(self, *args, **kwargs):
        super(RestartRequest, self).__init__(*args, **kwargs)

    def perform(self):
        self_info = WorkerInfo()
        if self.target in (self_info.name, self_info.ip):
            logger.warning('Restarting worker process by reason [%s]' % self.reason)
            Worker().restart()
