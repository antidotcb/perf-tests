__author__ = 'Danylo Bilyk'

import time

import pika

import protocol
from .json_message import JsonMessage
from pt.utils import log


def _generate_default_properties(message, reply_on=None, expiration=None, reply_to=None):
    if isinstance(reply_on, JsonMessage):
        reply_on = reply_on.id

    reply_on = str(reply_on)

    return pika.spec.BasicProperties(
        app_id='pt-protocol',
        content_encoding='utf-8',
        content_type='application/json',
        correlation_id=reply_on,
        expiration=expiration,
        message_id=message.id,
        reply_to=reply_to,
        timestamp=time.time(),
        type=protocol.get_message_type(message)
    )


class Sender(object):
    def __init__(self, connection, exchange, default_send_to='', default_reply_to=None, default_expiration=None):
        self._channel = connection.new_channel()
        self._exchange = exchange
        self._default_reply_to = str(default_reply_to)
        self._default_send_to = str(default_send_to)
        self._default_expiration = default_expiration

    def send(self, message, to='', reply_on=None, reply_to=None, expire=None):
        send_to = str(to) if to else self._default_send_to
        reply_to = str(reply_to) if reply_to else self._default_reply_to
        expiration = expire if expire else self._default_expiration

        if isinstance(message, JsonMessage):
            properties = _generate_default_properties(message, reply_on, expiration, reply_to)
            json = protocol.encode_message(message)
            self._channel.basic_publish(exchange=self._exchange, routing_key=send_to, body=json, properties=properties)
            log.debug('Sent message:')
            log.debug('target: %s', to)
            log.debug('message_id: %s', properties.message_id)
            log.debug('type: %s', properties.type)
            log.debug('reply_on: %s', properties.correlation_id)
            log.debug('reply_to: %s', properties.reply_to)
            log.debug('body: %s\n', json)
        else:
            raise TypeError('Unsupported protocol message type')
