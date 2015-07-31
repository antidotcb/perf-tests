__author__ = 'Danylo Bilyk'

from pt.protocol import Response

from pt.protocol import ProtocolMessage


class BackupResponse(Response):
    __metaclass__ = ProtocolMessage

    def __init__(self, *args, **kwargs):
        super(BackupResponse, self).__init__(*args, **kwargs)
