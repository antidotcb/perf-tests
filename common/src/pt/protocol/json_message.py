__author__ = 'Danylo Bilyk'

from datetime import datetime


def default_time():
    return datetime.now()


def class_lookup(cls):
    bases = list(cls.__bases__)
    for base in bases:
        bases.extend(class_lookup(base))
    return bases


class JsonMessage(object):
    _DEFAULTS = {
    }

    def __init__(self, *args, **kwargs):
        self._setup_defaults()
        self.set_values(kwargs)
        for arg in args:
            if isinstance(arg, dict):
                self.set_values(arg)
            elif isinstance(arg, object):
                self.set_values(arg.__dict__)
        for attr in self._DEFAULTS.keys():
            if attr not in self.__dict__:
                default = self._DEFAULTS[attr]
                if default and hasattr(default, '__call__'):
                    default = default()
                setattr(self, attr, default)

    def set_values(self, values):
        if not isinstance(values, dict):
            raise TypeError('')
        for attr, value in values.iteritems():
            if str(attr).startswith('_'):
                continue
            if attr in self._DEFAULTS.keys():
                setattr(self, attr, value)

    def _setup_defaults(self):
        self._DEFAULTS = self._DEFAULTS
        for base in class_lookup(self.__class__):
            _DEFAULTS = getattr(base, '_DEFAULTS', [])
            for attr in _DEFAULTS:
                if attr not in self._DEFAULTS.keys():
                    self._DEFAULTS[attr] = _DEFAULTS[attr]

    def __str__(self):
        return str(self.__dict__)
