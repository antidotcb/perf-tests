__author__ = 'Danylo Bilyk'

import cmd
from threading import *

from pt import RabbitConnection
from pt.protocol import Sender, Listener
from pt.utils import Config, logger
from pt.request import DiscoveryRequest, RestartRequest
from pt.processors import ResponseProcessor, ServerState


class Orchestrator(cmd.Cmd):
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
        self._state = ServerState()
        self._sender = Sender(self._connection, self._out_exchange)
        self.do_discovery()

    def start(self):
        for t in self._jobs:
            t.start()
        for t in self._jobs:
            t.join()

    # noinspection PyUnusedLocal
    def do_stop(self, *args):
        for t in self._jobs:
            try:
                # noinspection PyProtectedMember
                t._Thread__stop()
            except Exception, e:
                print('%s could not be terminated. Exception: %s' % (t.getName(), e))
        self._connection.close()
        return True

    # noinspection PyUnusedLocal
    def do_discovery(self, *args):
        self._sender.send(DiscoveryRequest())

    # noinspection PyUnusedLocal
    def do_status(self, *args):
        if len(args) and (args[0] == 'workers' or not len(args[0])) or not args:
            print 'Discovered workers: '
            workers = sorted(self._state.workers, key=lambda x: x.ip)
            format = '%s %s'
            if workers:
                longest_name_worker = max(workers, key=lambda worker: len(worker.name))
                format = '%{0}s %s'.format(len(longest_name_worker.name))
            print '\n'.join([format % (worker.name, worker.ip) for worker in workers])

    def do_restart(self, *args):
        all = self._state.workers
        selected = all
        if len(args) and args[0] != '*':
            worker_names = [str(worker.name) for worker in all]
            worker_ips = [str(worker.ip) for worker in all]
            selected_names = [name for name in args if name in worker_names]
            selected_by_name = [worker for worker in all if worker.name in selected_names]
            selected_ips = [ip for ip in args if ip in worker_ips]
            selected_by_ip = [worker for worker in all if worker_ips in selected_ips]
            incorrect = [arg for arg in args if arg not in worker_ips and arg not in selected_names]
            selected = list(set(selected_by_name) | set(selected_by_ip))
            logger.debug('Restarting names: %s', ', '.join([worker.name for worker in selected]))
            if incorrect:
                logger.warn('Unknown names: %s', ', '.join(incorrect))
        for worker in selected:
            self._sender.send(RestartRequest(target=worker.ip))
