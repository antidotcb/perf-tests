__author__ = 'antidotcb'

import pika
from bson import json_util

from pt.utils.protocol import Protocol


class Listener:
    def __init__(self, config):
        self._protocol = Protocol()
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(config.server()))
        self._channel = self._connection.channel()
        self._exchange = self._channel.exchange_declare(exchange='fan-out', type='fanout')
        self._queue = self._channel.queue_declare(exclusive=True)
        self._channel.queue_bind(exchange='fan-out', queue=self._queue_name())
        self._channel.basic_consume(self.callback, queue=self._queue_name(), no_ack=True)

    def _queue_name(self):
        return self._queue.method.queue

    def run(self):
        print ' [*] Waiting for requests. To exit press CTRL+C'
        self._channel.start_consuming()

    def callback(self, channel, method, properties, body):
        print " [x] body: %r" % (body)
        print " [-] channel: ", (channel)
        print " [-] method: ", (method)
        print " [-] properties: ", (properties)
        print ""
        try:
            parsed = dict(json_util.loads(body))
            print parsed
            message = self._protocol.create(dict(parsed))
            print message
        #     print self._protocol.create(dict(parsed)).to_json()
        except Exception as e:
            print e.errno, e.strerror
