__author__ = 'Danylo Bilyk'

import cmd
import threading
from pt import log

import pt

DISCOVERY_REQUEST_TIMEOUT = 2
EXECUTE_REQUEST_TIMEOUT = 10


class Terminal(cmd.Cmd):
    def __init__(self, orc):
        cmd.Cmd.__init__(self)
        self.prompt = ''
        self.orc = orc

    def do_stop(self, _args):
        pt.disable_auto_restart()
        self.orc.stop()

    def do_discovery(self, *args):
        self.orc.forget_all()
        self.orc.send_discovery_request()
        threading.Timer(DISCOVERY_REQUEST_TIMEOUT + 1, lambda: self.do_status()).start()

    def do_script(self, args):
        args = args.split()
        if len(args) < 2:
            log.error('Usage: script name target')
        else:
            args = args[0:2]
            script, target = args
            self.orc.execute_script(script, target)

    def do_status(self, *args):
        print 'Discovered: '
        # noinspection PyProtectedMember
        workers = self.orc._workers
        ips = sorted(workers, key=lambda w: (w[1].group, w[1].ip))
        mask = '%s\t%s\t%s\t\t%s'
        print '\n'.join([mask % (worker.name, worker.ip, worker.group, uuid) for uuid, worker in ips])

    def do_restart(self, *args):
        self.orc.restart_workers(args)

    def cmdloop(self, intro=None):
        cmd.Cmd.cmdloop(self, intro)


class Orchestrator(object):
    def __init__(self):
        self._terminal = Terminal(self)

        self.info = pt.WorkerInfo.own()

        self._conn = pt.Connection(**pt.config.connection())

        exchanges = pt.config.exchanges()

        self._conn.create_exchange(exchanges['broadcast'], 'fanout')
        self._conn.create_exchange(exchanges['direct'], 'direct', durable=True)

        self._listener = pt.protocol.Listener(self._conn, exchanges['direct'], self.processor,
                                              routing_key=self.info.uuid)

        self._broadcast = pt.protocol.Sender(self._conn, exchanges['broadcast'], default_reply_to=self.info.uuid)
        self._direct = pt.protocol.Sender(self._conn, exchanges['direct'], default_reply_to=self.info.uuid)

        self._workers = pt.WorkersCollection()

        self.__protect = threading.RLock()
        self._responses = {}
        self._targets = {}

        self.__threads = pt.ThreadCollection()
        self.__threads.add(self._listener.start)
        self.__threads.add(self._terminal.cmdloop)

        log.info('Own UUID: %s', self.info.uuid)

    def processor(self, response, properties):
        if isinstance(response, pt.protocol.Response):
            request_id = properties.correlation_id
            if request_id:
                with self.__protect:
                    responses = self._responses[request_id]
                    packed = (response, properties)
                    responses.append(packed)
                    self._responses[request_id] = responses
            else:
                # probably only case is greeting discovery response set as 'Hello'
                if isinstance(response, pt.DiscoveryResponse):
                    # TODO: do something with hello messages
                    pass

    def start(self):
        self.__threads.start()
        self.send_discovery_request()
        self.__threads.join()

    def stop(self):
        self._listener.stop()
        self.__threads.stop()
        self._conn.close()

    def send_broadcast_request(self, request):
        self._broadcast.send(request)
        self.add_request(request)

    def send_direct_request(self, request, to):
        if not isinstance(to, list):
            to = [to]

        for target in to:
            self._direct.send(request, to=target)

        self.add_request(request, to)

    def add_request(self, request, to=None):
        self._targets[request.id] = to
        self._responses[request.id] = []

    def forget_all(self):
        self._workers.reset()
        self._responses = {}
        self._targets = {}

    def send_discovery_request(self):
        request = pt.DiscoveryRequest()
        self.send_broadcast_request(request)
        timer = threading.Timer(DISCOVERY_REQUEST_TIMEOUT, lambda: self.on_discovery_timeout(request))
        timer.start()
        timer.join()

    def on_discovery_timeout(self, request):
        # targets = self._targets[request.id]
        responses = self._responses[request.id]

        for packed in responses:
            response, properties = packed
            if isinstance(response, pt.DiscoveryResponse):
                try:
                    accepted = self._workers.append(response)
                    if not accepted:
                        log.info('Shutdown identical worker: %s', response.uuid)
                        self._direct.send(pt.TerminateRequest(), to=response.uuid)
                except ValueError, e:
                    log.error('%s', e)
            else:
                log.error('Invalid response on discovery request')

        del self._targets[request.id]
        del self._responses[request.id]

    def execute_script(self, script, target=None):
        if not target:
            log.error('No targets specified. Won\'t send request to nobody')
            return

        targets = None
        if target:
            search_by_group = self._workers.find(group=target)
            search_by_name = self._workers.find(name=target)
            search_by_uuid = self._workers.find(uuid=target)
            search_by_ip = self._workers.find(ip=target)
            if search_by_group:
                targets = [worker.uuid for worker in search_by_group]
            elif search_by_name:
                targets = [worker.uuid for worker in search_by_name]
            elif search_by_ip:
                targets = [worker.uuid for worker in search_by_name]
            elif search_by_uuid:
                targets = [worker.uuid for worker in search_by_name]
            else:
                log.error('Can\'t find worker to execute script: %s', target)
                return

        request = pt.ExecuteRequest(script=script)
        self.send_direct_request(request, to=targets)
        callback = lambda: self.on_script_timeout(request)
        timer = threading.Timer(EXECUTE_REQUEST_TIMEOUT, callback)
        timer.start()
        timer.join()

    def on_script_timeout(self, request):
        # targets = self._targets[request.id]
        responses = self._responses[request.id]

        for packed in responses:
            response, properties = packed
            if isinstance(response, pt.ExecuteResponse):
                print response
            else:
                log.error('Invalid response on discovery request')

        del self._targets[request.id]
        del self._responses[request.id]

    def restart_workers(self, workers, reason=None):
        selected = []

        for worker in workers:
            found = self._workers.find(name=worker)
            for w in found:
                selected.append(w.uuid)
            if not found:
                log.warning('Unknown target: %s', worker)

        request = pt.RestartRequest(reason=reason)
        self.send_direct_request(request, to=selected)
