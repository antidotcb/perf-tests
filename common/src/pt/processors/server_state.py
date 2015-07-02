__author__ = 'Danylo Bilyk'

from pt.utils import Singleton
from .worker_info import WorkerInfoCollection


class ServerState(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.workers = WorkerInfoCollection()
