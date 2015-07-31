__author__ = 'Danylo Bilyk'

import time

from .discovery import Discovery
from .terminal import Terminal
from pt import config, log
import pt


class Orchestrator(object):
    def __init__(self):
        self._test_in_progress = False
        self._test_start_time = None

        self._verbose = False
        self._terminal = Terminal(self)

        self.config = config

        self._connection = pt.Connection(**self.config.connection())

        exchanges = self.config.exchanges()

        self._connection.create_exchange(exchanges['broadcast'], 'fanout')
        self._connection.create_exchange(exchanges['direct'], 'direct', durable=True)

        uuid = self.config.uuid()

        self._listener = pt.protocol.Listener(self._connection, exchanges['direct'], self.process, routing_key=uuid)
        self._broadcast = pt.protocol.Sender(self._connection, exchanges['broadcast'], default_reply_to=uuid)
        self._direct = pt.protocol.Sender(self._connection, exchanges['direct'], default_reply_to=uuid)

        self._workers = pt.Workers()
        self._discovery = Discovery(self, self._workers)

        self._states = {}

        self.__threads = pt.ThreadCollection()
        self.__threads.add(self._discovery.perform)
        self.__threads.add(self._listener.start)
        self.__threads.add(self._terminal.start)

    def process(self, response, properties):
        request_id = properties.correlation_id
        if request_id:
            if request_id in self._states.keys():
                request_state = self._states[request_id]
                request_state.collect_response(response, properties)
            else:
                log.error('Response to unknown request (request_id=%s): %s', request_id, response)
        else:
            log.warning('Response without request id: %s', response)

    def run(self):
        self.__threads.start()
        self.__threads.join()

    def stop(self):
        self._listener.stop()
        self._discovery.stop()
        self._connection.close()

    def _send_request(self, sender, request, targets=None, collect_cb=None, timeout_cb=None):
        state = pt.protocol.RequestState(request, targets, timeout_cb, collect_cb)
        self._states[request.id] = state
        sender.send(request, targets)
        return state

    def send_discovery_request(self):
        request = pt.DiscoveryRequest()
        return self._send_request(self._broadcast, request)

    def terminate_workers(self, targets):
        self._direct.send(pt.TerminateRequest(), targets=targets)

    def send_execute_request(self, script, targets, cb=None):
        if not targets:
            raise ValueError('Can\'t find worker to execute script: %s', targets)
        collect_cb = lambda response, properties: self.on_script_collect(script, response)
        request = pt.ExecuteRequest(script=script)
        return self._send_request(self._direct, request, targets, collect_cb, cb)

    def on_script_collect(self, script, resp):
        if resp.result and self._verbose:
            log.info('Worker %s finished script %s execution: %d\n%s', resp.name, script, resp.result, resp.output)
        else:
            log.info('Worker %s finished script %s execution: %d', resp.name, script, resp.result)
        return True

    def send_backup_request(self, targets, cb=None):
        request = pt.BackupRequest(test_start_time=self._test_start_time)
        return self._send_request(self._direct, request, targets, timeout_cb=cb)

    def restart_targets(self, targets, reason=None):
        request = pt.RestartRequest(reason=reason)
        self._direct.send(request, targets)

    def get_workers(self):
        return self._workers.all()

    def search_workers(self, query):
        return self._workers.search(query)

    def start_test(self):
        if self._test_in_progress:
            raise Exception('Test already in progress. Started %s' % time.ctime(self._test_start_time))
        self._test_start_time = time.time()
        self._test_in_progress = True
