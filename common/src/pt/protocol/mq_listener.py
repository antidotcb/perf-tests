__author__ = 'Danylo Bilyk'

from pt.utils import log
from pt.protocol import protocol


class Listener(object):
    def __init__(self, connection, exchange, processor, ack=True, **kwargs):
        if not hasattr(processor, '__call__'):
            raise TypeError('Processor should be a callable')

        self._processor = processor
        self._no_ack = not ack

        self._channel = connection.new_channel()

        self._queue = self._channel.queue_declare(exclusive=True)
        queue_name = self._queue.method.queue

        self._channel.queue_bind(exchange=exchange, queue=queue_name, **kwargs)
        self._consumer_tag = self._channel.basic_consume(self.callback, queue=queue_name, no_ack=self._no_ack)

    def start(self):
        self._channel.start_consuming()

    def stop(self):
        self._channel.stop_consuming(self._consumer_tag)

    # noinspection PyUnusedLocal
    def callback(self, channel, method, properties, body):
        # log.debug('channel: %s', channel.__dict__)
        # log.debug('method: %s', method.__dict__)
        log.debug('properties: %s', properties.__dict__)
        log.debug('body: %s', body)
        if self._processor:
            try:
                message = protocol.decode_message(body, properties)
                self._processor(message, properties)
                if not self._no_ack:
                    channel.basic_ack(delivery_tag=method.delivery_tag)
            except Exception, e:
                log.exception('Processor failed: %s', e)
