__author__ = 'Danylo Bilyk'

from pt.protocol.response import Response

from pt.utils import logger
from pt.protocol import ProtocolMessage
from pt.utils.server_state import ServerState
from pt.utils.worker_info import WorkerInfo


class DiscoveryResponse(Response):
    __metaclass__ = ProtocolMessage

    def __init__(self, *args, **kwargs):
        super(DiscoveryResponse, self).__init__(*args, **kwargs)
        self._server = ServerState()

    def collect(self):
        super(DiscoveryResponse, self).collect()
        self._server.workers.add(WorkerInfo(self.client, self.ip))
