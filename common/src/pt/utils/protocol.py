__author__ = 'antidotcb'

from .singleton import Singleton

class Protocol:
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
            print ' [x] registered message:', type_name
            self.definition[unicode(type_name)] = type

    def typename(self, type):
        type = unicode(str(type))
        return type[type.find('\'')+1:type.rfind('\'')]

    def type(self, typename):
        return self.definition[typename]

    def create(self, json):
        typename = json['__class__']
        type = self.type(typename)
        message = type(json)
        return message