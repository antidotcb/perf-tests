__author__ = 'Danylo Bilyk'

from pt import RabbitConnection
from pt.protocol import Listener, Sender
from pt.utils import Config, Singleton
from pt.processors import RequestProcessor
from pt.scenarios import restart


class Worker(object):
    __metaclass__ = Singleton

    def __init__(self):
        self._config = Config()

        self._options = Config().get_options(Config.CONNECTION_SECTION)
        self._connection_options = Config().get_options(Config.CONNECTION_SECTION)
        self._exchanges = Config().get_options(Config.EXCHANGE_SECTION)

        self._connection = RabbitConnection(self._connection_options)
        in_exchange = self._exchanges['request']
        out_exchange = self._exchanges['report']

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
