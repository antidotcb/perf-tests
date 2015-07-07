__author__ = 'Danylo Bilyk'

from bson import json_util

from pt.protocol import Protocol
from pt.utils import logger


class ResponseProcessor(object):
    def __init__(self):
        super(ResponseProcessor, self).__init__()
        self._catalog = Protocol()

    def process(self, channel, method, properties, body):
        try:
            json = dict(json_util.loads(body))
            response = self._catalog.create(json)
            if response:
                response.collect()
        except Exception, e:
            logger.exception('Exception occurred: %s', e)
        return None
