__author__ = 'Danylo Bilyk'

from .terminal import Terminal
from pt import config, log
import pt

DISCOVERY_TIMEOUT = 5
EXECUTION_TIMEOUT = 60


class CollectOnly(object):
    def __init__(self, cls):
        self.cls = cls

    # noinspection PyUnusedLocal
    def __call__(self, response, *args, **kwargs):
        return isinstance(response, self.cls)


class Orchestrator(object):
    def __init__(self):
        self.verbose = False
        self._terminal = Terminal(self)

        self.config = config

        self._conn = pt.Connection(**self.config.connection())

        exchanges = self.config.exchanges()

        self._conn.create_exchange(exchanges['broadcast'], 'fanout')
        self._conn.create_exchange(exchanges['direct'], 'direct', durable=True)

        uuid = self.config.uuid()

        self._listener = pt.protocol.Listener(self._conn, exchanges['direct'], self.process, routing_key=uuid)
        self._broadcast = pt.protocol.Sender(self._conn, exchanges['broadcast'], default_reply_to=uuid)
        self._direct = pt.protocol.Sender(self._conn, exchanges['direct'], default_reply_to=uuid)

        self._active_workers = pt.Workers()
        self._discovered_responses = []

        self._states = {}

        self.__threads = pt.ThreadCollection()
        self.__threads.add(self._perform_discovery)
        self.__threads.add(self._listener.start)
        self.__threads.add(self._terminal.start)

    def process(self, response, properties):
        if isinstance(response, pt.protocol.Response):
            request_id = properties.correlation_id
            if request_id:
                if request_id in self._states.keys():
                    request_state = self._states[request_id]
                    request_state.collect_response(response, properties)
                else:
                    log.error('Response to unknown request (request_id=%s): %s', request_id, response)
            else:
                log.warning('Response without request id: %s', response)

    def start(self):
        self.__threads.start()
        self.__threads.join()

    def stop(self):
        self._listener.stop()
        self.__threads.stop()
        self._conn.close()

    def send_request(self, sender, targets, timeout, request, collect_cb=None, responded_cb=None, timeout_cb=None):
        state = pt.protocol.RequestState(timeout, request, targets, timeout_cb, collect_cb, responded_cb)
        self._states[state.request.id] = state
        sender.send(state.request, target=targets)
        return state

    def _perform_discovery(self):
        request = pt.DiscoveryRequest()
        timeout = DISCOVERY_TIMEOUT
        collector = CollectOnly(pt.DiscoveryResponse)
        while True:
            request_state = self.send_request(self._broadcast, '', timeout, request, collect_cb=collector)
            request_state.wait_for_responses()
            lost = self._active_workers.all()
            new = {}
            for detail in request_state.get_response_details():
                r = detail.response
                discovered = pt.Worker(r.name, r.ip, r.group, r.uuid)
                if discovered.uuid in self._active_workers:
                    worker = self._active_workers[discovered.uuid]
                    if worker == discovered:
                        del lost[discovered.uuid]
                        continue
                    if worker.ip != discovered.ip:
                        log.error('CRITICAL ERROR: Duplicate UUID for different IP. Terminating.\nOld:%s\nNew:%s',
                                  worker, discovered)
                        raise pt.DuplicateError()
                    else:
                        log.debug('Renamed worker: %s ==> %s', worker, discovered)
                        self._active_workers.remove(worker.uuid)
                        self._active_workers.append(discovered)
                else:
                    new[discovered.uuid] = discovered

            for lost_worker_uuid in lost.keys():
                self._active_workers.remove(lost_worker_uuid)

            duplicates = []
            for new_worker in new.values():
                try:
                    self._active_workers.append(new_worker)
                    mask = pt.Worker(name=new_worker.name, ip=new_worker.ip, group=new_worker.group)
                    lost_after_restart = [worker for worker in lost.values() if worker.match(mask)]
                    if lost_after_restart:
                        old = lost_after_restart[0]
                        del lost[old.uuid]
                        log.debug('Restart detected: %s', new_worker)
                    else:
                        log.info('Found new worker: %s', new_worker)
                except pt.DuplicateError, e:
                    duplicates.append(new_worker.uuid)
                    log.error(e)

            for lost_worker in lost.values():
                log.warning('Lost connection to: %s', lost_worker)

    def terminate_workers(self, targets):
        self._direct.send(pt.TerminateRequest(), target=targets)

    def send_execute_request(self, script, targets, cb=None):
        if not targets:
            raise ValueError('Can\'t find worker to execute script: %s', targets)
        collect_cb = lambda response, properties: self.on_script_collect(script, response)
        timeout = EXECUTION_TIMEOUT
        request = pt.ExecuteRequest(script=script)
        return self.send_request(self._direct, targets, timeout, request, collect_cb, cb)

    def on_script_collect(self, script, resp):
        if resp.result and self.verbose:
            log.info('Worker %s finished script %s execution: %d\n%s', resp.name, script, resp.result, resp.output)
        else:
            log.info('Worker %s finished script %s execution: %d', resp.name, script, resp.result)

    def restart_targets(self, targets, reason=None):
        request = pt.RestartRequest(reason=reason)
        self._direct.send(request, target=targets)

    def get_workers(self):
        return self._active_workers

    def search_targets(self, query):
        found = self._active_workers.search(query)
        if found:
            return [worker.uuid for worker in found]
        else:
            return []
