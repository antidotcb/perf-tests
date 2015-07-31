__author__ = 'Danylo Bilyk'

from protocol import Protocol


class ProtocolMessage(type):
    def __new__(mcs, class_name, bases, attrs):
        new_class = super(ProtocolMessage, mcs).__new__(mcs, class_name, bases, attrs)
        if not Protocol.is_registered(new_class):
            Protocol.register_message_type(new_class)
        return new_class
