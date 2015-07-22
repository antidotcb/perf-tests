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
        self._collection = {}

    def append(self, info):
        same_ip = self.find(ip=info.ip)
        if same_ip:
            identical = self.find(group=info.group, name=info.name, collection=same_ip)
            if identical:
                log.warning('Won\'t append similar worker to collection, probably just several identical instances.')
                return False
        else:
            self._collection[info.uuid] = WorkerInfo(info.name, info.ip, info.group, info.uuid)
            return True

    def find(self, name=None, ip=None, group=None, uuid=None, collection=None):
        if not collection:
            collection = [item for uuid, item in self._collection.items()]
        found = [item for item in collection if
                 (
                     (item.name == name or not name) and
                     (item.ip == ip or not ip) and
                     (item.group == group or not group) and
                     (item.uuid == uuid or not uuid)
                 )]
        return found

    def reset(self):
        self._collection.clear()

    def remove(self, uuid):
        del self._collection[uuid]

    def __iter__(self):
        return iter(self._collection.items())
