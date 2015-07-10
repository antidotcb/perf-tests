__author__ = 'Danylo Bilyk'

import cmd
from threading import *

from pt import mq_connection
from pt.protocol import Sender, Listener
from pt.utils import config, log, workers, enable_auto_restart, disable_auto_restart
from pt.request import DiscoveryRequest, RestartRequest, ExecuteRequest
from pt.processors import ResponseProcessor


class Orchestrator(cmd.Cmd):
    def __init__(self):
        enable_auto_restart(10)
        cmd.Cmd.__init__(self)

        connection_options = config.get_options(config.CONNECTION_SECTION)
        exchanges = config.get_options(config.EXCHANGE_SECTION)

        self._connection = mq_connection
        self._connection.init(connection_options)
        self._out_exchange = exchanges['broadcast']
        self._in_exchange = exchanges['direct']

        self._connection.create_exchange(self._out_exchange, 'fanout')
        self._connection.create_exchange(self._in_exchange, 'direct', durable=True)

        self._listener = Listener(self._connection, self._in_exchange, ResponseProcessor().process)
        self._jobs = []
        self._jobs.append(Thread(target=self._listener.start))
        self._jobs.append(Thread(target=self.cmdloop))
        self._sender = Sender(self._connection, self._out_exchange)
        self.do_discovery()

    def start(self):
        for t in self._jobs:
            t.start()
        for t in self._jobs:
            t.join()

    # noinspection PyUnusedLocal
    def do_stop(self, *args):
        self._listener.stop()
        for t in self._jobs:
            try:
                # noinspection PyProtectedMember
                t._Thread__stop()
            except Exception, e:
                print('%s could not be terminated. Exception: %s' % (t.getName(), e))
        self._connection.close()
        disable_auto_restart()
        return True

    # noinspection PyUnusedLocal
    def do_discovery(self, *args):
        workers.reset()
        self._sender.send(DiscoveryRequest())

    # noinspection PyUnusedLocal
    def do_status(self, *args):
        if len(args) and (args[0] == 'workers' or not len(args[0])) or not args:
            print 'Discovered workers: '
            ips = sorted(workers, key=lambda x: x.ip)
            mask = '%s %s'
            if ips:
                longest_name_worker = max(ips, key=lambda worker: len(worker.name))
                mask = '%{0}s %s'.format(len(longest_name_worker.name))
            print '\n'.join([mask % (worker.name, worker.ip) for worker in ips])

    def do_restart(self, *args):
        selected = workers
        if len(args) and args[0] and args[0] != '*':
            worker_names = [str(worker.name) for worker in workers]
            worker_ips = [str(worker.ip) for worker in workers]
            selected_names = [name for name in args if name in worker_names]
            selected_by_name = [worker for worker in workers if worker.name in selected_names]
            selected_ips = [ip for ip in args if ip in worker_ips]
            selected_by_ip = [worker for worker in workers if worker_ips in selected_ips]
            incorrect = [arg for arg in args if arg not in worker_ips and arg not in selected_names]
            selected = list(set(selected_by_name) | set(selected_by_ip))
            log.debug('Restarting names: %s', ', '.join([worker.name for worker in selected]))
            if incorrect:
                log.warn('Unknown names: %s', ', '.join(incorrect))
        for worker in selected:
            self._sender.send(RestartRequest(target=worker.ip))

    def do_update(self, *args):
        self._sender.send(ExecuteRequest(script='.scripts\\update_src.bat'))

    def do_mt4_start(self, *args):
        self._sender.send(ExecuteRequest(script='scripts\\mt4_start.bat'))

    def do_mt4_stop(self, *args):
        self._sender.send(ExecuteRequest(script='scripts\\mt4_stop.bat'))

    def do_mt4_query(self, *args):
        self._sender.send(ExecuteRequest(script='scripts\\mt4_query.bat'))

    def do_mt4_clean(self, *args):
        self._sender.send(ExecuteRequest(script='scripts\\mt4_clean.bat'))

    def do_mt4_clean_logs(self, *args):
        self._sender.send(ExecuteRequest(script='scripts\\mt4_clean_logs.bat'))
