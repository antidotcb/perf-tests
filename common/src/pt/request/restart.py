__author__ = 'Danylo Bilyk'

from pt.protocol.request import Request
from pt.protocol import ProtocolMessage
from pt.worker import Worker
from pt.utils import logger


class RestartRequest(Request):
    __metaclass__ = ProtocolMessage

    _FIELDS = {
        'reason': None,
    }

    def __init__(self, *args, **kwargs):
        super(RestartRequest, self).__init__(*args, **kwargs)

    def perform(self):
        if self._is_target():
            logger.warn('Restarting worker process by reason [%s]' % self.reason)
            Worker().restart()
