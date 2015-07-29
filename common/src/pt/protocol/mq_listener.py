__author__ = 'Danylo Bilyk'

from pt.utils import log
from pt.protocol import protocol


class Listener(object):
    def __init__(self, connection, exchange, processor, ack=True, **kwargs):
        if not processor or not callable(processor):
            raise TypeError('Processor should be a callable')

        self._processor = processor
        self._no_ack = not ack

        self._channel = connection.new_channel()

        self._queue = self._channel.queue_declare(exclusive=True)
        self._queue_name = self._queue.method.queue
        log.info('Created queue (queue: %s)', self._queue_name)

        self._channel.queue_bind(exchange=exchange, queue=self._queue_name, **kwargs)
        log.info('Queue bind (exchange: %s, queue: %s, args=%s)', exchange, self._queue_name, kwargs)
        self._tag = self._channel.basic_consume(self.callback, queue=self._queue_name, no_ack=self._no_ack)
        log.debug('Consumer tag created (tag: %s, queue: %s)', self._tag, self._queue_name)

    def start(self):
        number = self._channel.channel_number
        log.info('Start consuming (number: %s, queue: %s, tag: %s)', number, self._queue_name, self._tag)
        self._channel.start_consuming()

    def stop(self):
        number = self._channel.channel_number
        self._channel.stop_consuming(self._tag)
        log.info('Stop consume (number: %s, queue: %s, tag: %s)', number, self._queue_name, self._tag)
        self._channel.close()

    # noinspection PyUnusedLocal
    def callback(self, channel, method, properties, body):
        log.debug('Received message:')
        log.debug(' type: %s', properties.type)
        log.debug(' message_id: %s', properties.message_id)
        log.debug(' correlation_id: %s', properties.correlation_id)
        log.debug(' reply_to: %s', properties.reply_to)
        log.debug(' body:\n%s\n', body)
        try:
            message = protocol.decode_message(body, properties)
            self._processor(message, properties)
            if not self._no_ack:
                tag = method.delivery_tag
                channel.basic_ack(delivery_tag=tag)
                log.debug('Acknowledge sent (ch: %s, delivery_tag: %s)', self._channel.channel_number, tag)
        except Exception, e:
            log.exception('Processor failed: %s', e)
