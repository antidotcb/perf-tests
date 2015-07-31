__author__ = 'Danylo Bilyk'

from collections import deque

import pt
from pt import log


class Discovery(object):
    def __init__(self, orchestrator, workers):
        self._orchestrator = orchestrator
        self._active = True
        self._workers = workers
        self._lost_workers = deque(maxlen=100)

    def perform(self):
        while self._active:
            request_state = self._orchestrator.send_discovery_request()
            request_state.wait_for_responses()
            self.process_responses(request_state)

    def process_responses(self, request_state):
        responses = [detail.response for detail in request_state.get_response_details()]
        lost_workers = {worker.uuid: worker for worker in self._workers if worker.uuid not in request_state.responded()}
        create_worker = lambda r: pt.Worker(r.name, r.ip, r.group, r.uuid)
        worker_ids = self._workers.ids()
        fresh_workers = [create_worker(response) for response in responses if response.uuid not in worker_ids]

        for lost_worker in lost_workers.keys():
            self._workers.remove(lost_worker)

        new_workers = {}
        for fresh_worker in fresh_workers:
            try:
                if fresh_worker.uuid in self._workers:
                    worker = self._workers[fresh_worker.uuid]
                    if worker.ip != fresh_worker.ip:
                        raise pt.DuplicateError(
                            'Duplicate UUID for different IP. Old:%s New:%s' % (worker, fresh_worker))
                self._workers.append(fresh_worker)
                new_workers[fresh_worker.uuid] = fresh_worker
            except pt.DuplicateError, e:
                log.error(e)

        self._lost_workers.extend(lost_workers.values())

        if len(self._lost_workers):
            for fresh_worker in self._workers:
                mask = pt.Worker(name=fresh_worker.name, ip=fresh_worker.ip, group=fresh_worker.group)
                lost_and_found = [worker for worker in self._lost_workers if worker.match(mask)]
                if lost_and_found:
                    for restarted_worker in lost_and_found:
                        self._lost_workers.remove(restarted_worker)
                        log.debug('Restarted worker: %s', restarted_worker)
                        uuid = restarted_worker.uuid
                        if uuid in lost_workers.keys():
                            del lost_workers[uuid]
                        if fresh_worker.uuid in new_workers.keys():
                            del new_workers[fresh_worker.uuid]

        for lost_worker in lost_workers.values():
            log.error('Lost connection to worker: %s', lost_worker)
            self._lost_workers.remove(lost_worker)

        for new_worker in new_workers.values():
            log.info('Discovered worker: %s', new_worker)

    def stop(self):
        self._active = False
