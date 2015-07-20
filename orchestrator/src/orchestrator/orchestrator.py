__author__ = 'Danylo Bilyk'

import cmd

import pt
from pt import log

DEFAULT_REQUEST_TIMEOUT = 10


# noinspection PyUnusedLocal,PyClassicStyleClass
class Orchestrator(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = ''

        self.info = pt.WorkerInfo.own()

        self._conn = pt.Connection(**pt.config.connection())

        exchanges = pt.config.exchanges()

        self._conn.create_exchange(exchanges['broadcast'], 'fanout')
        self._conn.create_exchange(exchanges['direct'], 'direct')

        self._direct = pt.protocol.Listener(self._conn, exchanges['direct'], self.processor, routing_key='orc')

        self._broadcast = pt.protocol.Sender(self._conn, exchanges['broadcast'])
        self._sender = pt.protocol.Sender(self._conn, exchanges['direct'])

        self._workers = pt.WorkersCollection()

        self._responses = {}
        self._requests = {}

        self.__threads = pt.ThreadCollection()
        self.__threads.append(self._direct.start)
        self.__threads.append(self.cmdloop)

    def processor(self, response, properties):
        request_id = properties.correlation_id
        if request_id in self._requests.keys():
            responses = []
            if request_id in self._responses.keys():
                responses = self._responses[request_id]
            packed = (response, properties)
            responses.append(packed)
            self._responses[request_id] = responses

    def start(self):
        self.__threads.start()
        self.do_discovery()
        self.__threads.join()

    def stop(self):
        self._direct.stop()
        self.__threads.stop()
        self._conn.close()

    def _send_request(self, request):
        properties = self._broadcast.send(request, reply_to='orc')
        self._requests[properties.message_id] = (request, properties)
        tc = self.__threads.timeout_callback(DEFAULT_REQUEST_TIMEOUT, self.on_discovery_timeout, properties.message_id)

    def on_discovery_timeout(self, request_id):
        request, properties = self._requests[request_id]
        del self._requests[request_id]
        responses = self._responses[request_id]
        for packed in responses:
            response, properties = packed
            if isinstance(response, pt.DiscoveryResponse):
                self._workers.append(response.client, response.ip, response.group)
            else:
                log.error('Invalid response for Discovery')
        self.do_status()

    def do_stop(self, *args):
        self.stop()
        pt.disable_auto_restart()
        return True

    def do_discovery(self, *args):
        self._workers.reset()
        self._send_request(pt.DiscoveryRequest())

    def do_status(self, *args):
        print 'Discovered: '
        ips = sorted(self._workers, key=lambda x: x.ip)
        mask = '%s %s'
        if ips:
            longest_name_worker = max(ips, key=lambda w: len(w.name))
            mask = '%{0}s %s'.format(len(longest_name_worker.name))
        print '\n'.join([mask % (worker.name, worker.ip) for worker in ips])

    def do_restart(self, *args):
        workers = self._workers
        selected = self._workers
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
            self._broadcast.send(pt.RestartRequest(target=worker.ip))

    def do_update(self, *args):
        self._broadcast.send(pt.ExecuteRequest(script='update_src'))
