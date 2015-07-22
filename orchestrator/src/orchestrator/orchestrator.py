__author__ = 'Danylo Bilyk'

import cmd
from optparse import OptionParser
from pt import log

import pt

DISCOVERY_TIMEOUT = 2
EXECUTION_TIMEOUT = 10


class Terminal(cmd.Cmd):
    def __init__(self, orc):
        cmd.Cmd.__init__(self)
        self.prompt = ''
        self.orc = orc
        self.context = None

    def precmd1(self, line):
        parts = line.split(':')
        # target is specified at start and separated from command by semicolon
        args = line.split()
        target = None
        if len(parts) > 1:
            target = parts[0]
            args = parts[1:]
        else:
            parser = OptionParser()
            parser.add_option('target', dest='target')
            options, unparsed_args = parser.parse_args(line.split)
            if options.target:
                target = options.target
                args = unparsed_args

        if target:
            # found some target, check if it exists
            targets = self.orc.find_targets(target)
            if targets:
                self.set_context(targets)
            else:
                log.error('Cannot find target workers: %s', target)
        else:
            # no execution target specified, processing line as it is
            self.set_context(None)

        line = ''.join(args)
        return line

    def set_context(self, context):
        self.context = context

    def do_stop(self, _args):
        pt.disable_auto_restart()
        self.orc.stop()

    def do_discovery(self, *args):
        self.orc.perform_discovery()
        self.do_status()

    def do_script(self, args):
        args = args.split()
        if len(args) < 2:
            log.error('Usage: script name target')
            return
        args = args[0:2]
        script, target = args
        targets = self.orc.find_targets(target)
        state = self.orc.send_execute_request(script, targets)
        state.wait_for_responses()

    def do_status(self, *args):
        print 'Discovered: '
        # noinspection PyProtectedMember
        workers = self.orc._workers
        self.print_workers(workers)

    def print_workers(self, workers):
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

        self._states = {}

        self.__threads = pt.ThreadCollection()
        self.__threads.add(self._listener.start)
        self.__threads.add(self._terminal.cmdloop)

        log.info('Own UUID: %s', self.info.uuid)

    def processor(self, response, properties):
        if isinstance(response, pt.protocol.Response):
            request_id = properties.correlation_id
            if request_id:
                request_state = self._states[request_id]
                request_state.collect_response(response, properties)

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

    def send_request(self, sender, targets, timeout, request, collect_cb=None, responded_cb=None, timeout_cb=None):
        state = pt.protocol.RequestState(timeout, request, targets, timeout_cb, collect_cb, responded_cb)
        self._states[state.request.id] = state
        sender.send(state.request, target=targets)
        return state

    def perform_discovery(self):
        self._workers.reset()
        request_state = self.send_discovery_request()
        request_state.wait_for_responses()

    def send_discovery_request(self, cb=None):
        collect = lambda response, properties: self.on_discovery_collect(response, properties)
        return self.send_request(self._broadcast, '', DISCOVERY_TIMEOUT, pt.DiscoveryRequest(), collect, cb)

    def on_discovery_collect(self, response, *args):
        if not isinstance(response, pt.DiscoveryResponse):
            return False
        accepted = False
        try:
            accepted = self._workers.append(response)
        except ValueError, e:
            log.error('Cannot add discovered worker [%s]. Exception: %s', response.uuid, e)
        if not accepted:
            log.warning('Shutdown identical worker: %s', response.uuid)
            self._direct.send(pt.TerminateRequest(), target=response.uuid)
        else:
            log.info('Discovered: %s\t%s\t%s\t%s', response.name, response.group, response.ip, response.uuid)

    def send_execute_request(self, script, targets, cb=None):
        if not targets:
            raise ValueError('Can\'t find worker to execute script: %s', targets)
        collect_cb = lambda response, properties: self.on_script_collect(script, response, properties)
        return self.send_request(self._direct, targets, EXECUTION_TIMEOUT, pt.ExecuteRequest(script=script), collect_cb,
                                 cb)

    def on_script_collect(self, script, resp, properties):
        log.info('Worker %s finished script %s execution: [%s] %s', resp.name, script, resp.result, resp.output)

    def restart_workers(self, target, reason=None):
        selected = []

        for worker in target:
            found = self._workers.find(name=worker)
            for w in found:
                selected.append(w.uuid)
            if not found:
                log.warning('Unknown target: %s', worker)

        request = pt.RestartRequest(reason=reason)
        self._direct.send(request, target=selected)

    def find_targets(self, target):
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
        return targets
