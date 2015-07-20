__author__ = 'Danylo Bilyk'

import socket

from pt.utils import log, config


class WorkerInfo(object):
    def __init__(self, name=None, ip=None, group=None):
        self.name = name
        self.ip = ip
        self.group = group

    @staticmethod
    def own(group='workers'):
        ip = socket.gethostbyname(socket.gethostname())
        name = config.get('name')
        group = group if group else config.get('group')
        return WorkerInfo(name, ip, group)


class WorkersCollection(object):
    def __init__(self):
        self._list = []

    def append(self, name, ip, group):
        same_name = any(x.name == name for x in self._list)
        if same_name:
            same_ip = any(x.ip == ip and x.name == name for x in self._list)
            if same_ip:
                log.debug('Worker %s with IP %s already known.', name, ip)
            else:
                raise AttributeError('List already contains worker %s with similar name but different ip' % name)
        else:
            self._list.append(WorkerInfo(name, ip, group))

    def reset(self):
        del self._list[:]

    def __iter__(self):
        return iter(self._list)
