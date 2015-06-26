__author__ = 'Danylo Bilyk'

from bson import json_util

from .processor import MessageProcessor
from pt.protocol import *
from pt.utils import logger


class RequestProcessor(MessageProcessor):
    def __init__(self, sender):
        self._census = Census()
        self._sender = sender

    def process(self, channel, method, properties, body):
        try:
            json = dict(json_util.loads(body))
            message = self._census.create(json)
            response = message.perform()
            if response and sender and isinstance(response, JsonMessage):
                self._sender.send(reponse)
        except Exception, e:
            logger.exception('Exception occured: %s', e)
        return None
