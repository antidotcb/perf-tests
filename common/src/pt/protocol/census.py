__author__ = 'Danylo Bilyk'

from pt.utils import Singleton
from pt.utils import logger


class Census:
    __metaclass__ = Singleton

    def __init__(self):
        self.definition = {}

    def list(self):
        return self.definition.keys()

    def get(self, name):
        return self.definition[name]

    def contains(self, type):
        return (type in self.definition)

    def add(self, type):
        type_name = self.typename(type)
        if 'JsonMessage' not in type_name:
            logger.debug('Registered protocol message type: %s', type_name)
            self.definition[unicode(type_name)] = type

    def typename(self, type):
        type = unicode(str(type))
        return type[type.find('\'') + 1:type.rfind('\'')]

    def type(self, typename):
        return self.definition[typename]

    def class_id(self):
        return '_id'

    def create(self, json):
        type_name = None
        try:
            type_name = json[self.class_id()]
        except Exception, e:
            logger.exception('Field %s not found. JSON: %s', e, json)
        if not type_name:
            raise TypeError('Message type is empty.' % self.class_id())
        class_name = self.type(type_name)
        if not class_name:
            raise LookupError('Census message type not registered: %s' % type_name)
        message = class_name(json)
        return message
