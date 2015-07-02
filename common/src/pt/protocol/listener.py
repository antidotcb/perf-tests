__author__ = 'Danylo Bilyk'

from .message_catalog import MessageCatalog
from pt.utils import logger


class Listener(object):
    def __init__(self, connection, exchange, processor, ack=True, **kwargs):
        if not hasattr(processor, '__call__'):
            raise TypeError('Processor should be a callable')

        self._catalog = MessageCatalog()
        self._processor = processor
        self._channel = connection.channel
        self._ack = ack

        self._queue = self._channel.queue_declare(exclusive=True)
        self._channel.queue_bind(exchange=exchange, queue=self._queue_name(), **kwargs)

        self._consumer_tag = self._channel.basic_consume(self.callback, queue=self._queue_name(), no_ack=not self._ack)

    def _queue_name(self):
        return self._queue.method.queue

    def start(self):
        self._channel.start_consuming()

    def stop(self):
        self._channel.stop_consuming(self._consumer_tag)

    def callback(self, channel, method, properties, body):
        # logger.debug('channel: %s', channel)
        # logger.debug('method: %s', method)
        # logger.debug('properties: %s', properties)
        # logger.debug('body: %s', body)
        if self._processor:
            try:
                self._processor(channel, method, properties, body)
                if self._ack:
                    channel.basic_ack(delivery_tag=method.delivery_tag)
            except Exception, e:
                logger.exception('Processor failed: %s', e)
