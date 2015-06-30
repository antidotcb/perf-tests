__author__ = 'Danylo Bilyk'

import socket

from .response import Response
from pt.protocol import RegisteredMessage
from pt.utils import Config, logger


def client_id():
    name = Config().get('name')
    return name


def client_ip():
    ip = socket.gethostbyname(socket.gethostname())
    return ip


class DiscoveryResponse(Response):
    __metaclass__ = RegisteredMessage

    _FIELDS = {
        'client': client_id,
        'ip': client_ip
    }

    def __init__(self, *args, **kwargs):
        super(DiscoveryResponse, self).__init__(*args, **kwargs)

    def collect(self):
        logger.info('Collected response: %s', self.to_json())
