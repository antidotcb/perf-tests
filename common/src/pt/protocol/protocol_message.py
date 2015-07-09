__author__ = 'Danylo Bilyk'

import protocol


class ProtocolMessage(type):
    def __new__(mcs, class_name, bases, attrs):
        new_class = super(ProtocolMessage, mcs).__new__(mcs, class_name, bases, attrs)
        if not protocol.is_registered(new_class):
            protocol.register_message_type(new_class)
        return new_class
