__author__ = 'Danylo Bilyk'

from pt.protocol import Response

from pt.protocol import ProtocolMessage
from pt.utils import workers, WorkerInfo


class DiscoveryResponse(Response):
    __metaclass__ = ProtocolMessage

    _DEFAULTS = {
        'request_uuid': None
    }

    def __init__(self, *args, **kwargs):
        super(DiscoveryResponse, self).__init__(*args, **kwargs)

    def collect(self):
        super(DiscoveryResponse, self).collect()
        workers.add(WorkerInfo(self.client, self.ip))
