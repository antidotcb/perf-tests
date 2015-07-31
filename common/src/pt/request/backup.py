__author__ = 'Danylo Bilyk'

import time

from pt.protocol import Request
from pt.protocol import ProtocolMessage
from pt.response import BackupResponse


class BackupRequest(Request):
    __metaclass__ = ProtocolMessage

    _TIMEOUT = 1800  # seconds
    _RESPONSE = BackupResponse

    def __init__(self, *args, **kwargs):
        self.test_start_time = time.time()
        super(BackupRequest, self).__init__(*args, **kwargs)
