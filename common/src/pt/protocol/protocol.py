__author__ = 'Danylo Bilyk'

from pt.utils import log
from bson import json_util

definition = {}
class_id = '_id'

def is_registered(type_name):
    return type_name in definition


def register_message_type(type_name):
    name = typename(type_name)
    log.debug('Registered protocol message type: %s', name)
    definition[name] = type_name


def typename(type_name):
    type_name = unicode(str(type_name))
    return type_name[type_name.find('\'') + 1:type_name.rfind('\'')]


def find_msg_type(type_name):
    return definition[type_name]


def message_from_json(json):
    try:
        type_name = json[class_id]
        return construct(type_name, json)
    except Exception, e:
        log.exception('Field %s not found. JSON: %s', e, json)


def message_to_json(message):
    d = {k: message.__dict__[k] for k in message.__dict__ if not str(k).startswith('_')}
    d[class_id] = typename(message.__class__)
    return json_util.dumps(d, sort_keys=True, default=json_util.default)

def construct(type_name, *arg, **kwargs):
    if not type_name:
        raise TypeError('Message type is empty')
    class_name = find_msg_type(type_name)
    if not class_name:
        raise LookupError('Protocol message type not registered: %s' % type_name)
    message = class_name(*arg, **kwargs)
    return message
