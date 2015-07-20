__author__ = 'Danylo Bilyk'

from pt.utils import config, log


class WorkerInfo(object):
    def __init__(self, name=None, ip=None, group=None, uuid=None):
        self.name = name
        self.ip = ip
        self.group = group
        self.uuid = uuid

    @staticmethod
    def own():
        own_group = config.get('group')
        own_ip = config.get('ip')
        own_name = config.get('name')
        own_uuid = config.get('uuid')
        return WorkerInfo(own_name, own_ip, own_group, own_uuid)


class WorkersCollection(object):
    def __init__(self):
        self._collection = []

    def append(self, name, ip, group, uuid):
        same_ip = self.find(ip=ip)
        if same_ip:
            identical = self.find(group=group, name=name, collection=same_ip)
            if identical:
                log.warning('Won\'t append similar worker to collection, probably just several identical instances.')
                return False
            else:
                raise ValueError('Only one worker is allowed per machine: found=%s, trying to add (%s, %s)',
                                 same_ip[0].__dict__, name, group)
        else:
            self._collection.append(WorkerInfo(name, ip, group, uuid))
            return True

    def find(self, name=None, ip=None, group=None, uuid=None, collection=None):
        if not collection:
            collection = self._collection
        found = [x for x in collection if
                 (
                     (x.name == name or not name) and
                     (x.ip == ip or not ip) and
                     (x.group == group or not group) and
                     (x.uuid == uuid or not uuid)
                 )]
        return found

    def reset(self):
        del self._collection[:]

    def __iter__(self):
        return iter(self._collection)
