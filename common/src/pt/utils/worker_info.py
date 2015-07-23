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
        own_group = config.get_option('group')
        own_ip = config.get_option('ip')
        own_name = config.get_option('name')
        own_uuid = config.get_option('uuid')
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
            collection = [item for uuid_, item in self._collection.items()]
        found = []
        for item in collection:
            _name = (item.name == name or not name)
            _ip = (item.ip == ip or not ip)
            _group = (item.group == group or not group)
            _uuid = (item.uuid == uuid or not uuid)
            if _name and _ip and _group and _uuid:
                found.append(item)
        return found

    def reset(self):
        self._collection.clear()

    def remove(self, uuid):
        del self._collection[uuid]

    def __iter__(self):
        return iter(self._collection.itervalues())

    def __getitem__(self, key):
        return self._collection[key]
