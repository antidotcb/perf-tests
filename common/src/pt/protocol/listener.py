__author__ = 'antidotcb'

from .census import Census
from pt.processors import MessageProcessor
from pt.utils import logger


class Listener:
    def __init__(self, connection, exchange, processor):
        if not isinstance(processor, MessageProcessor):
            raise TypeError('Processor should be a MessageProcessor subclass')

        self._census = Census()
        self._processor = processor
        self._channel = connection.channel

        self._queue = self._channel.queue_declare(exclusive=True)
        self._channel.queue_bind(exchange=exchange, queue=self._queue_name())
        self._channel.basic_consume(self.callback, queue=self._queue_name(), no_ack=False)

    def _queue_name(self):
        return self._queue.method.queue

    def start(self):
        logger.info(' [*] Waiting for requests. To exit press CTRL+C')
        self._channel.start_consuming()

    def callback(self, channel, method, properties, body):
        if self._processor:
            try:
                self._processor.process(channel, method, properties, body)
                channel.basic_ack(delivery_tag=method.delivery_tag)
            except Exception, e:
                logger.exception('Processor failed: %s', e)
