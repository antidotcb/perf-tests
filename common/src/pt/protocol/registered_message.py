__author__ = 'Danylo Bilyk'

from .message_catalog import MessageCatalog


class RegisteredMessage(type):
    def __new__(mcs, class_name, bases, attrs):
        new_class = super(RegisteredMessage, mcs).__new__(mcs, class_name, bases, attrs)
        protocol = MessageCatalog()
        if not protocol.contains(new_class):
            protocol.add(new_class)
        return new_class
