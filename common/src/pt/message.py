__author__ = 'Danylo Bilyk'

import json
from datetime import datetime

def default_time():
    return datetime.now()

class JsonMessage(object):
    FIELDS = {
        'timestamp': default_time
    }

    def __init__(self):
        for attr in self.FIELDS.keys():
            setattr(self, attr, self.FIELDS[attr])

    def _get_fields(self):
        result = self.FIELDS
        if self.__class__ is not JsonMessage:
            for attr in super(JsonMessage, self)._get_fields():
                if attr not in self.FIELDS:
                    result[attr] = super_fields[attr]
        return result

    def to_json(self):
        return json.dumps(self.__dict__)

    def from_json(self, json_message):
        result = json.loads(json)
        for attr, value in result.__dict__.iteritems():
            if attr in self.FIELDS.keys():
                self[attr] = value
        return self

