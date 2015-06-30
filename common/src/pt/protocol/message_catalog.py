__author__ = 'Danylo Bilyk'

from pt.utils import Singleton
from pt.utils import logger


class MessageCatalog(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.definition = {}
        self.class_id = '_id'

    def list(self):
        return self.definition.keys()

    def get(self, name):
        return self.definition[name]

    def contains(self, type_name):
        return type_name in self.definition

    def add(self, type_name):
        name = self.typename(type_name)
        logger.debug('Registered protocol message type: %s', name)
        self.definition[unicode(name)] = type_name

    @staticmethod
    def typename(type_name):
        type_name = unicode(str(type_name))
        return type_name[type_name.find('\'') + 1:type_name.rfind('\'')]

    def type(self, typename):
        return self.definition[typename]

    def create(self, json):
        try:
            type_name = json[self.class_id]
            return self.construct(type_name, json)
        except Exception, e:
            logger.exception('Field %s not found. JSON: %s', e, json)

    def construct(self, type_name, *arg, **kwargs):
        if not type_name:
            raise TypeError('Message type is empty')
        class_name = self.type(type_name)
        if not class_name:
            raise LookupError('MessageCatalog message type not registered: %s' % type_name)
        message = class_name(*arg, **kwargs)
        return message
