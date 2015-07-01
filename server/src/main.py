__author__ = 'Danylo Bilyk'

import cmd
from pt import RabbitConnection, ResponseProcessor, Sender, Listener, DiscoveryRequest, Config

from threading import *

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
        self._jobs.append(Thread(target=self._listener.start))
        self._jobs.append(Thread(target=self.cmdloop))

    def run(self):
        for t in self._jobs:
            t.start()
        for t in self._jobs:
            t.join()

    # noinspection PyUnusedLocal
    def do_stop(self, *args):
        for t in self._jobs:
            try:
                t._Thread__stop()
            except Exception, e:
                print('%s could not be terminated. Exception: %s' % (t.getName(), e))
        self._connection.close()
        return True

    # noinspection PyUnusedLocal
    def do_discovery(self, *args):
        request_sender = Sender(self._connection, self._out_exchange)
        request_sender.send(DiscoveryRequest())


if __name__ == '__main__':
    server = Server()
    server.run()
