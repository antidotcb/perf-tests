__author__ = 'Danylo Bilyk'

import time

import pika

from protocol import Protocol
from .json_message import JsonMessage
from pt.utils import log, Worker


class Sender(object):
    def __init__(self, connection, exchange, default_targets=None, default_reply_to=None, default_expiration=None):
        self._channel = connection.new_channel()
        self._exchange = exchange
        self._reply_to = Sender.__to_string(default_reply_to)
        if default_targets:
            if not isinstance(default_targets, list):
                default_targets = [default_targets]
            for target in default_targets:
                if not isinstance(target, Worker):
                    raise TypeError('Only workers are accepted as target')
        self._targets = default_targets
        self._expiration = default_expiration

    def send(self, message, targets=None, reply_on=None, reply_to=None, expiration=None):
        targets = targets or self._targets
        reply_to = self.__to_string(reply_to, self._reply_to)
        expiration = expiration if expiration else self._expiration

        if not isinstance(targets, list):
            targets = [targets]

        for target in targets:
            if target and not isinstance(target, Worker):
                raise TypeError('Only workers are accepted as target')

        if isinstance(message, JsonMessage):
            msg_properties = self.__generate_properties(message, reply_on, expiration, reply_to)
            json = Protocol.encode_message(message)
            for target in targets:
                key = target.uuid if target else ''
                try:
                    self._channel.basic_publish(self._exchange, routing_key=key, body=json, properties=msg_properties)
                    self.__print_debug_info(json, msg_properties, target)
                except Exception, e:
                    log.error('Error trying to send: %s', e)
                    log.error('target: %s', target)
                    log.error('message_id: %s', msg_properties.message_id)
                    log.error('type: %s', msg_properties.type)
                    log.error('reply_on: %s', msg_properties.correlation_id)
                    log.error('reply_to: %s', msg_properties.reply_to)
                    log.error('body: %s\n', json)
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
            type=Protocol.get_message_type(message.__class__)
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

    @staticmethod
    def __to_string(value, default_value=''):
        return str(value) if value else default_value
