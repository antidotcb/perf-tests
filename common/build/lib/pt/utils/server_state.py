__author__ = 'Danylo Bilyk'

from .worker_info import WorkerInfoCollection
from pt.utils import Singleton


class ServerState(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.workers = WorkerInfoCollection()
