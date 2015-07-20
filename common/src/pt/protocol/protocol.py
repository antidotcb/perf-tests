__author__ = 'Danylo Bilyk'

import inspect

from bson import json_util

from pt.utils import log

definition = {}


def is_registered(type_name):
    return type_name in definition


def register_message_type(type_name):
    name = get_message_type(type_name)
    log.debug('Registered protocol message type: %s', name)
    definition[name] = type_name


def get_message_type(type_name):
    if not inspect.isclass(type_name):
        if isinstance(type_name, object):
            type_name = type_name.__class__
    type_name = unicode(str(type_name))
    return type_name[type_name.find('\'') + 1:type_name.rfind('\'')]


def find_message_type(type_name):
    return definition[type_name]


def decode_message(body, properties):
    json = dict(json_util.loads(body))
    try:
        type_name = properties.type
        return construct(type_name, json)
    except Exception, e:
        log.exception('Field %s not found. JSON: %s', e, json)


def encode_message(message):
    d = {k: message.__dict__[k] for k in message.__dict__ if not str(k).startswith('_')}
    return json_util.dumps(d, sort_keys=True, default=json_util.default)


def construct(type_name, *arg, **kwargs):
    if not type_name:
        raise TypeError('Message type is empty')
    class_name = find_message_type(type_name)
    if not class_name:
        raise LookupError('Protocol message type not registered: %s' % type_name)
    message = class_name(*arg, **kwargs)
    return message
