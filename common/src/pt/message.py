__author__ = 'Danylo Bilyk'

from datetime import datetime
import json

from bson import json_util


def default_time():
    return datetime.now()


class JsonMessage(object):
    DEFAULTS = {
        'timestamp': default_time
    }

    def __init__(self, *args, **kwargs):
        self.setup_default()
        self.set_values(kwargs)
        for arg in args:
            if isinstance(arg, dict):
                self.set_values(arg)
            elif isinstance(arg, object):
                self.set_values(arg.__dict__)
        for attr in self.DEFAULTS.keys():
            if attr not in self.__dict__:
                default = self.DEFAULTS[attr]
                if hasattr(default, '__call__'):
                    default = default()
                setattr(self, attr, default)

    def set_values(self, fields):
        allowed = self.DEFAULTS.keys()
        for attr in fields.keys():
            if attr in allowed:
                setattr(self, attr, fields[attr])
            else:
                if attr != 'DEFAULTS':
                    raise AttributeError('Attribute `%s` is not allowed' % attr)

    def setup_default(self):
        self.DEFAULTS = self.DEFAULTS
        for base in self.__class__.__bases__:
            defaults = getattr(base, 'DEFAULTS', [])
            for attr in defaults:
                if attr not in self.DEFAULTS.keys():
                    self.DEFAULTS[attr] = defaults[attr]

    def to_json(self):
        d = self.__dict__.copy()
        del d['DEFAULTS']
        d['__class__'] = str(self.__class__)
        return json_util.dumps(d, sort_keys=True, indent=4, default=json_util.default)

    def from_json(self, str):
        result = json_util.loads(str)
        for attr, value in result.iteritems():
            if attr in self.DEFAULTS.keys():
                setattr(self, attr, value)
        if 'tzinfo' in self.__dict__:
            del self.__dict__['tzinfo']


    def __str__(self):
        return str(self.__dict__)
