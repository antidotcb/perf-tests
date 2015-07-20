__author__ = 'Danylo Bilyk'

import uuid
import time

import pika

import protocol
from .json_message import JsonMessage
from pt.utils import log, WorkerInfo


def default_properties(message, correlation_id=None, expiration=None, reply_to=None):
    return pika.spec.BasicProperties(
        app_id='pt-protocol',
        cluster_id=WorkerInfo.own().group,
        content_encoding='utf-8',
        content_type='application/json',
        correlation_id=correlation_id,
        expiration=expiration,
        message_id=str(uuid.uuid4()),
        reply_to=reply_to,
        timestamp=time.time(),
        type=protocol.get_message_type(message),
    )


class Sender(object):
    def __init__(self, connection, exchange, default_send_to='', default_reply_to=None, default_expiration=None):
        self._channel = connection.new_channel()
        self._exchange = exchange
        self._default_reply_to = default_reply_to
        self._default_send_to = default_send_to
        self._default_expiration = default_expiration

    def send(self, message, to='', reply_on=None, reply_to=None, expire=None):
        send_to = to if to else self._default_send_to
        reply_to = reply_to if reply_to else self._default_reply_to
        expiration = expire if expire else self._default_expiration

        if isinstance(message, JsonMessage):
            props = default_properties(message, reply_on, expiration, reply_to)
            json = protocol.encode_message(message)
            self._channel.basic_publish(exchange=self._exchange, routing_key=send_to, body=json, properties=props)
            log.debug('Sent: to=%s, body=%s, props=%s', send_to, json, props)
            return props
        else:
            raise TypeError('Unsupported protocol message type')
