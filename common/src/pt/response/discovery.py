__author__ = 'Danylo Bilyk'

from .response import Response

from pt.utils import logger
from pt.protocol import ProtocolMessage
from pt.processors.server_state import ServerState
from pt.processors.worker_info import WorkerInfo


class DiscoveryResponse(Response):
    __metaclass__ = ProtocolMessage

    _FIELDS = {
        'client': WorkerInfo.own().name,
        'ip': WorkerInfo.own().ip
    }

    def __init__(self, *args, **kwargs):
        super(DiscoveryResponse, self).__init__(*args, **kwargs)
        self._server = ServerState()

    def collect(self):
        logger.info('Collected response: %s', self.to_json())
        self._server.workers.add(WorkerInfo(self.client, self.ip))
