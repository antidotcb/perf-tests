__author__ = 'Danylo Bilyk'

from pt.utils.protocol import Protocol


class ProtocolMessage(type):
    def __new__(cls, clsname, bases, attrs):
        newclass = super(ProtocolMessage, cls).__new__(cls, clsname, bases, attrs)
        protocol = Protocol()
        if not protocol.contains(newclass):
            protocol.add(newclass)
        return newclass
