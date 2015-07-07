__author__ = 'Danylo Bilyk'

import socket

from pt.utils import logger, Config


class WorkerInfo(object):
    def __init__(self, name=None, ip=None):
        self.name = name
        self.ip = ip

    @staticmethod
    def own():
        name = Config().get('name')
        ip = socket.gethostbyname(socket.gethostname())
        return WorkerInfo(name, ip)


class WorkerInfoCollection(object):
    def __init__(self):
        self._list = []

    def add(self, worker):
        if not isinstance(worker, WorkerInfo):
            raise TypeError('Incorrect type')
        same_name = any(x.name == worker.name for x in self._list)
        if same_name:
            same_ip = any(x.ip == worker.ip and x.name == worker.name for x in self._list)
            if same_ip:
                logger.debug('Worker %s with IP %s already known:', worker.name, worker.ip)
            else:
                raise AttributeError('List already contains worker %s with similar name but different ip' % worker.name)
        else:
            self._list.append(worker)

    def reset(self):
        del self._list[:]

    def __iter__(self):
        return iter(self._list)
