__author__ = 'Danylo Bilyk'

from .json_message import JsonMessage
from pt.utils import logger


class Sender(object):
    def __init__(self, connection, exchange, default_key=''):
        self._channel = connection.channel
        self._exchange = exchange
        self._key = default_key

    def send(self, message, routing_key=''):
        key = self._key
        if routing_key:
            key = routing_key
        if isinstance(message, JsonMessage):
            json = message.to_json()
            logger.debug('Sending json: %s', json)
            self._channel.basic_publish(exchange=self._exchange, routing_key=key, body=json)
        else:
            raise TypeError('Unsupported protocol message type')