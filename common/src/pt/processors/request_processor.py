__author__ = 'Danylo Bilyk'

from bson import json_util

from pt.protocol import MessageCatalog
from pt.request import Request
from pt.utils import logger


class RequestProcessor(object):
    def __init__(self, sender):
        super(RequestProcessor, self).__init__()
        self._catalog = MessageCatalog()
        self._sender = sender

    def process(self, channel, method, properties, body):
        try:
            json = dict(json_util.loads(body))
            request = self._catalog.create(json)

            if isinstance(request, Request):
                response = request.perform()
                if response and self._sender:
                    self._sender.send(response)
        except Exception, e:
            logger.exception('Exception occurred: %s', e)
        return None
