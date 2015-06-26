__author__ = 'Danylo Bilyk'

from bson import json_util

from .processor import MessageProcessor
from pt.protocol import Census
from pt.utils import logger


class RequestProcessor(MessageProcessor):
    def __init__(self):
        self._protocol = Census()

    def process(self, channel, method, properties, body):
        logger.debug(' [+] body: %r', body)
        logger.debug(' [-] channel: %r', channel)
        logger.debug(' [-] method: %r', method)
        logger.debug(' [-] properties: %r', properties)
        try:
            json = dict(json_util.loads(body))
            message = self._protocol.create(json)
            return message
        except Exception, e:
            logger.exception('Exception occured: %s', e)
        return None
