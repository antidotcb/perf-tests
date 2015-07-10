__author__ = 'Danylo Bilyk'

from pt import mq_connection
from pt.protocol import Listener, Sender
from pt.utils import config
from pt.processors import RequestProcessor
from pt.scenarios import restart


class Worker(object):
    def __init__(self):
        self._connection_options = config.get_options(config.CONNECTION_SECTION)
        self._exchanges = config.get_options(config.EXCHANGE_SECTION)

        self._connection = mq_connection
        self._connection.init(self._connection_options)
        in_exchange = self._exchanges['broadcast']
        out_exchange = self._exchanges['direct']

        self._response_sender = Sender(self._connection, out_exchange)
        responder = RequestProcessor(self._response_sender)

        self._request_listener = Listener(self._connection, in_exchange, responder.process)

    def start(self):
        self._request_listener.start()

    def stop(self):
        self._request_listener.stop()
        self._connection.close()

    def restart(self):
        self.stop()
        restart()
