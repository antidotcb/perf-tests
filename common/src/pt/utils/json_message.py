__author__ = 'Danylo Bilyk'

from datetime import datetime

from bson import json_util

from .protocol import Protocol
from .protocol_message import ProtocolMessage


def default_time():
    return datetime.now()


class JsonMessage(object):
    __metaclass__ = ProtocolMessage

    _FIELDS = {
        'timestamp': default_time
    }

    def __init__(self, *args, **kwargs):
        self._protocol = Protocol()
        self.setup_default()
        self.set_values(kwargs)
        for arg in args:
            if isinstance(arg, dict):
                self.set_values(arg)
            elif isinstance(arg, object):
                self.set_values(arg.__dict__)
        for attr in self._FIELDS.keys():
            if attr not in self.__dict__:
                default = self._FIELDS[attr]
                if default is None:
                    continue
                if hasattr(default, '__call__'):
                    default = default()
                setattr(self, attr, default)

    def set_values(self, fields):
        allowed = self._FIELDS.keys()
        for attr in fields.keys():
            if str(attr).startswith('_'):
                continue
            if attr in allowed:
                setattr(self, attr, fields[attr])
            else:
                raise AttributeError('Attribute `%s` is not allowed' % attr)

    def setup_default(self):
        self._FIELDS = self._FIELDS
        for base in self.__class__.__bases__:
            _FIELDS = getattr(base, '_FIELDS', [])
            for attr in _FIELDS:
                if attr not in self._FIELDS.keys():
                    self._FIELDS[attr] = _FIELDS[attr]

    def to_json(self):
        d = {k: self.__dict__[k] for k in self.__dict__ if not str(k).startswith('_')}
        d[self._protocol.class_id()+'1'] = self._protocol.typename(self.__class__) + '1'
        return json_util.dumps(d, sort_keys=True, default=json_util.default)

    def from_json(self, str):
        result = json_util.loads(str)
        for attr, value in result.iteritems():
            if attr in self._FIELDS.keys():
                setattr(self, attr, value)

    def __str__(self):
        return str(self.__dict__)