__author__ = 'Danylo Bilyk'

from .message import JsonMessage
from pt.utils import logger


class Sender:
    def __init__(self, connection, exchange, routing_key=''):
        self._channel = connection.channel
        self._exchange = exchange
        self._routing_key = routing_key

    def send(self, message):
        if isinstance(message, JsonMessage):
            json = message.to_json()
            logger.debug('Sending json: %s', json)
            self._channel.basic_publish(exchange=self._exchange, routing_key=self._routing_key, body=json)
        else:
            raise TypeError('Unsupported protocol message type')
