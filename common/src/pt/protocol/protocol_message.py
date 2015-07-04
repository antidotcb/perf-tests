__author__ = 'Danylo Bilyk'

from .protocol import Protocol


class ProtocolMessage(type):
    def __new__(mcs, class_name, bases, attrs):
        new_class = super(ProtocolMessage, mcs).__new__(mcs, class_name, bases, attrs)
        protocol = Protocol()
        if not protocol.contains(new_class):
            protocol.add(new_class)
        return new_class
