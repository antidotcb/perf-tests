__author__ = 'Danylo Bilyk'

import cmd
from pt import log

import pt

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
        self._conn.create_exchange(exchanges['direct'], 'direct', durable=True)

        self._listener = pt.protocol.Listener(self._conn, exchanges['direct'], self.processor,
                                              routing_key=self.info.uuid)

        self._broadcast = pt.protocol.Sender(self._conn, exchanges['broadcast'])
        self._direct = pt.protocol.Sender(self._conn, exchanges['direct'])

        self._workers = pt.WorkersCollection()

        self._responses = {}
        self._requests = {}

        self.__threads = pt.ThreadCollection()
        self.__threads.append(self._listener.start)
        self.__threads.append(self.cmdloop)

    def processor(self, response, properties):
        request_id = properties.correlation_id
        if isinstance(response, pt.protocol.Response):
            if request_id not in self._requests.keys() and request_id:
                log.warning('Unrequested response detected: ignoring. Response: %s', response)
                return
            if request_id:
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
        self.do_discovery()
        self.__threads.join()

    def stop(self):
        self._listener.stop()
        self.__threads.stop()
        self._conn.close()

    def send_broadcast_request(self, request, callback=None):
        self.__send_request(request, self._broadcast, callback)
        self.add_request(request)
        self.register_callback(callback, request.id)

    def send_direct_request(self, request, to, callback=None):
        if not isinstance(to, list):
            to = [to]

        for target in to:
            self.__send_request(request, self._direct, callback=callback, to=target)

        self.add_request(request, to)
        self.register_callback(callback, request.id)

    def __send_request(self, request, sender, callback=None, to=''):
        return sender.send(request, reply_to=self.info.uuid, to=to)

    def add_request(self, request, to=None):
        if not to:
            to = []

        if request.id not in self._requests.keys():
            self._requests[request.id] = (request, to)
            self._responses[request.id] = []

    def register_callback(self, callback, *args, **kwargs):
        if callback:
            if not hasattr(callback, '__call__'):
                raise TypeError('Callback should be callable')
            tc = self.__threads.timeout_callback(DEFAULT_REQUEST_TIMEOUT, callback, *args, **kwargs)

    def on_discovery_timeout(self, request_id):
        request, send_to = self._requests[request_id]
        responses = self._responses[request_id]

        for packed in responses:
            response, properties = packed
            if isinstance(response, pt.DiscoveryResponse):
                try:
                    accepted = self._workers.append(response)
                    if not accepted:
                        log.info('Shutdown identical workers. it means they are same.')
                        self.__send_request(pt.TerminateRequest(), sender=self._direct, to=response.uuid)
                except ValueError, e:
                    log.error('%s', e)
            else:
                log.error('Invalid response on discovery request')
        self.do_status()

        del self._requests[request_id]
        del self._responses[request_id]

    def on_script_timeout(self, request_id):
        request, send_to = self._requests[request_id]
        responses = self._responses[request_id]

        for packed in responses:
            response, properties = packed
            if isinstance(response, pt.ExecuteResponse):
                print response
            else:
                log.error('Invalid response on discovery request')

        del self._requests[request_id]
        del self._responses[request_id]

    def do_stop(self, *args):
        self.stop()
        pt.disable_auto_restart()
        return True

    def do_discovery(self, *args):
        self._workers.reset()
        self.send_broadcast_request(pt.DiscoveryRequest(), callback=self.on_discovery_timeout)

    def do_script(self, *args):
        if not args[0]:
            log.error('No script name defined. Nothing to execute')
            return
        request = pt.ExecuteRequest(script='update_src')
        targets = [uuid for uuid, worker in self._workers]
        self.send_direct_request(request, to=targets, callback=self.on_script_timeout)

    def do_status(self, *args):
        print 'Discovered: '
        ips = sorted(self._workers, key=lambda x: x[1].ip)
        mask = '%s %s'
        if ips:
            uuid, longest_name = max(ips, key=lambda w: len(w[1].name))
            mask = '%{0}s %s %s'.format(len(longest_name.name))
        print '\n'.join([mask % (worker.name, worker.ip, uuid) for uuid, worker in ips])

    def do_restart(self, *args):
        workers = self._workers
        selected = []
        if not args[0]:
            selected = [uuid for uuid, worker in self._workers]
        else:
            for arg in args:
                found = self._workers.find(name=arg)
                for uuid, worker in found:
                    selected.append(uuid)
                if not found:
                    log.warning('Unknown target: %s', arg)

        for uuid in selected:
            self.send_direct_request(pt.RestartRequest(reason='by manual command'), to=uuid)

    def do_update(self, *args):
        self._broadcast.send(pt.ExecuteRequest(script='update_src'))
