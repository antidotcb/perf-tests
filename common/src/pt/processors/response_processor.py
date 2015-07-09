__author__ = 'Danylo Bilyk'

from bson import json_util

from pt.protocol import protocol
from pt.utils import log


class ResponseProcessor(object):
    def __init__(self):
        super(ResponseProcessor, self).__init__()

    def process(self, channel, method, properties, body):
        try:
            json = dict(json_util.loads(body))
            response = protocol.message_from_json(json)
            if response:
                response.collect()
        except Exception, e:
            log.exception('Exception occurred: %s', e)
        return None
