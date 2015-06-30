__author__ = 'Danylo Bilyk'

import cmd
from pt import RabbitConnection, ResponseProcessor, Sender, Listener, DiscoveryRequest, Config

import sys
import gevent
import gevent.select


class Server(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        # config = Config()

        # options = Config().get_options(Config.CONNECTION_SECTION)
        connection_options = Config().get_options(Config.CONNECTION_SECTION)
        exchanges = Config().get_options(Config.EXCHANGE_SECTION)

        self._connection = RabbitConnection(connection_options)
        self._out_exchange = exchanges['request']
        self._in_exchange = exchanges['report']

        self._connection.create_exchange(self._out_exchange, 'fanout')
        self._connection.create_exchange(self._in_exchange, 'fanout', durable=True)

        self._listener = Listener(self._connection, self._in_exchange, ResponseProcessor().process)
        self._jobs = []

    def start(self):
        self._jobs.append(gevent.spawn(self._listener.start))
        self.do_discovery()
        #self.cmdloop('Orchestrator:')
        gevent.wait(self._jobs)

    def do_stop(self, *args):
        gevent.killall(self._jobs)
        connection.close()
        return True

    def do_discovery(self, *args):
        request_sender = Sender(self._connection, self._out_exchange)
        request_sender.send(DiscoveryRequest())


if __name__ == '__main__':
    server = Server()
    server.start()
