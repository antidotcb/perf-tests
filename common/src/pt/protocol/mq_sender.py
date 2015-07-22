__author__ = 'Danylo Bilyk'

import time

import pika

import protocol
from .json_message import JsonMessage
from pt.utils import log


class Sender(object):
    def __init__(self, connection, exchange, default_send_to='', default_reply_to=None, default_expiration=None):
        self._channel = connection.new_channel()
        self._exchange = exchange
        self._own_address = str(default_reply_to)
        self._default_target = str(default_send_to)
        self._expiration = default_expiration

    def send(self, message, target='', reply_on=None, reply_to=None, expiration=None):
        targets = target if target else self._default_target
        reply_to = str(reply_to) if reply_to else self._own_address
        expiration = expiration if expiration else self._expiration

        if not isinstance(targets, list):
            targets = [targets]

        if isinstance(message, JsonMessage):
            properties = self.__generate_properties(message, reply_on, expiration, reply_to)
            json = protocol.encode_message(message)
            for target in targets:
                self._channel.basic_publish(self._exchange, target, json, properties)
                self.__print_debug_info(json, properties, target)
        else:
            raise TypeError('Unsupported protocol message type')

    @staticmethod
    def __generate_properties(message, source=None, expiration=None, reply_to=None):
        if isinstance(source, JsonMessage):
            source = source.id

        source = str(source)

        return pika.spec.BasicProperties(
            app_id='pt-protocol',
            content_encoding='utf-8',
            content_type='application/json',
            correlation_id=source,
            expiration=expiration,
            message_id=message.id,
            reply_to=reply_to,
            timestamp=time.time(),
            type=protocol.get_message_type(message)
        )

    @staticmethod
    def __print_debug_info(json, properties, target):
        log.debug('Sent message:')
        log.debug('target: %s', target)
        log.debug('message_id: %s', properties.message_id)
        log.debug('type: %s', properties.type)
        log.debug('reply_on: %s', properties.correlation_id)
        log.debug('reply_to: %s', properties.reply_to)
        log.debug('body: %s\n', json)
