__author__ = 'Danylo Bilyk'

import uuid


class JsonMessage(object):
    def __init__(self, *args, **kwargs):
        self.id = str(uuid.uuid4())
        for arg in args:
            if isinstance(arg, dict):
                self.__set_values(arg)
            elif isinstance(arg, object):
                self.__set_values(arg.__dict__)
            else:
                raise TypeError('Unnamed arguments are accepted only in form dictionaries or objects.')
        self.__set_values(kwargs)  # directly passed constructor args override any others

    def __set_values(self, values):
        if not isinstance(values, dict):
            raise TypeError('Values to setup should be a dictionary.')
        for attr, value in values.iteritems():
            if str(attr).startswith('_'):
                continue  # skip `private` members
            if str(attr) in self.__dict__.keys():
                setattr(self, attr, value)

    def __str__(self):
        return str(self.__dict__)
