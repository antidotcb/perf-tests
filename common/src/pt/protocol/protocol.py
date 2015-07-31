__author__ = 'Danylo Bilyk'

import inspect

from bson import json_util

from pt.utils import log


class Protocol(object):
    _definition = {}

    @staticmethod
    def is_registered(type_name):
        return type_name in Protocol._definition

    @staticmethod
    def register_message_type(type_name):
        if not inspect.isclass(type_name):
            raise TypeError('Can only register classes')
        name = Protocol.get_message_type(type_name)
        Protocol._definition[name] = type_name
        log.debug('Registered message type in protocol: %s', name)

    @staticmethod
    def get_message_type(type_name):
        type_name = unicode(str(type_name))
        return type_name[type_name.find('\'') + 1:type_name.rfind('\'')]

    @staticmethod
    def find_message_type(type_name):
        return

    @staticmethod
    def decode_message(body, type_name):
        json = json_util.loads(body)
        return Protocol.construct(type_name, json)

    @staticmethod
    def encode_message(message):
        d = {k: message.__dict__[k] for k in message.__dict__ if not str(k).startswith('_')}
        return json_util.dumps(d, sort_keys=True, default=json_util.default)

    @staticmethod
    def construct(type_name, *arg, **kwargs):
        if not type_name:
            raise TypeError('Message type is empty')
        if not Protocol.is_registered(type_name):
            raise LookupError('Protocol message type not registered: %s' % type_name)
        class_name = Protocol._definition[type_name]
        message = class_name(*arg, **kwargs)
        return message
