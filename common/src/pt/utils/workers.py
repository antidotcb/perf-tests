__author__ = 'Danylo Bilyk'


class Worker(object):
    def __init__(self, name=None, ip=None, group=None, uuid=None):
        self.name = name
        self.ip = ip
        self.group = group
        self.uuid = uuid

    def match(self, mask):
        return (
            (self.group == mask.group or mask.group is None or self.group is None) and
            (self.ip == mask.ip or mask.ip is None or self.ip is None) and
            (self.name == mask.name or mask.name is None or self.name is None) and
            (self.uuid == mask.uuid or mask.uuid is None or self.uuid is None)
        )

    def __eq__(self, obj):
        return (self.group == obj.group) and (self.ip == obj.ip) and (self.name == obj.name) and (self.uuid == obj.uuid)

    def __str__(self):
        return '%s\t%s\t%s\t%s' % (self.name, self.ip, self.group, self.uuid)


class DuplicateError(BaseException):
    def __init__(self, *args, **kwargs):
        super(DuplicateError, self).__init__(*args, **kwargs)


class Workers(object):
    def __init__(self):
        self._collection = {}

    def append(self, info):
        ip_mask = Worker(ip=info.ip)
        name_mask = Worker(name=info.name)

        worker_info = Worker(info.name, info.ip, info.group, info.uuid)

        similar_name = [worker for worker in self._collection.itervalues() if worker.match(ip_mask)]
        similar_ip = [worker for worker in self._collection.itervalues() if worker.match(name_mask)]
        if similar_name or similar_ip:
            raise DuplicateError('Worker with name %s already exists.' % worker_info)

        self._collection[info.uuid] = worker_info

    def remove(self, uid):
        if uid in self._collection.keys():
            del self._collection[uid]

    def all(self):
        return self._collection.copy()

    def search(self, query='*'):
        if not query:
            raise AttributeError('Empty query.')

        if query == '*':
            return self._collection.values()

        masks = (
            Worker(group=query),
            Worker(name=query),
            Worker(ip=query)
        )
        for mask in masks:
            masked = [worker for worker in self if worker.match(mask)]
            if masked:
                return masked

        return None

    def reset(self):
        self._collection.clear()

    def __iter__(self):
        return iter(self._collection.itervalues())

    def __contains__(self, item):
        return item in self._collection.keys()

    def __getitem__(self, key):
        return self._collection[key]
