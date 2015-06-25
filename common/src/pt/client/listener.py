__author__ = 'antidotcb'

from bson import json_util

from pt.utils.protocol import Protocol

from pt.processors import MessageProcessor

from pt.utils import logger


class Listener:
    def __init__(self, exchange, processor):
        if not isinstance(processor, MessageProcessor):
            raise TypeError('Listener message processor should be MessageProcessor type.')

        self._processor = processor
        self._config = Config()
        self._protocol = Protocol()
        self._channel = RabbitConnection().channel

        self._queue = self._channel.queue_declare(exclusive=True)
        self._channel.queue_bind(exchange=exchange, queue=self._queue_name())
        self._channel.basic_consume(self.callback, queue=self._queue_name(), no_ack=False)

    def _queue_name(self):
        return self._queue.method.queue

    def start(self):
        logger.info(' [*] Waiting for requests. To exit press CTRL+C')
        self._channel.start_consuming()

    def callback(self, channel, method, properties, body):
        logger.debug(' [+] body: %r', body)
        logger.debug(' [-] channel: %r', channel)
        logger.debug(' [-] method: %r', method)
        logger.debug(' [-] properties: %r', properties)
        try:
            if self._processor:
                self._processor.process(channel, method, properties, body)
            parsed = dict(json_util.loads(body))
            message = self._protocol.create(dict(parsed))
        except Exception, e:
            logger.exception('Exception occured: %s', e)

        channel.basic_ack(delivery_tag=method.delivery_tag)
