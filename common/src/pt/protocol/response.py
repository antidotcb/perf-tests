__author__ = 'Danylo Bilyk'

from pt.protocol import protocol, JsonMessage
from pt.utils import WorkerInfo, log


class Response(JsonMessage):
    _DEFAULTS = {
        'client': WorkerInfo.own().name,
        'group': config.own().group,
        'ip': WorkerInfo.own().ip
    }

    def __init__(self, *args, **kwargs):
        super(Response, self).__init__(*args, **kwargs)

    def collect(self):
        log.info('Collected response: %s', protocol.message_to_json(self))
