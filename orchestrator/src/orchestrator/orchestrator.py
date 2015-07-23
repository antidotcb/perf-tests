__author__ = 'Danylo Bilyk'

import time
import cmd
from pt import log

from tabulate import tabulate

import pt

DISCOVERY_TIMEOUT = 2
EXECUTION_TIMEOUT = 10


# noinspection PyUnusedLocal,PyClassicStyleClass
class Terminal(cmd.Cmd):
    no_cmd = ''

    def __init__(self, orc):
        cmd.Cmd.__init__(self)
        self.orc = orc
        self._default_targets = '*'
        self._command_targets = None
        self.update_prompt()

    def update_prompt(self):
        if self._default_targets:
            self.prompt = '[%s]:' % self._default_targets
        else:
            self.prompt = ':'

    def emptyline(self):
        pass

    def precmd(self, line):
        parts = line.split(':')
        # target is specified at start and separated from command by semicolon
        args = line.split()
        target = None
        if len(parts) > 1:
            target = parts[0]
            args = parts[1:]

        try:
            self._try_set_command_targets(target)
            if not args or (len(args) == 1 and not args[0].strip()):
                self.set_default_targets(target)
        except ValueError, e:
            log.error(e)
            return self.no_cmd

        if not self._command_targets:
            self._command_targets = self._default_targets

        new_line = ' '.join(args)
        return new_line

    def default(self, line):
        try:
            self._try_set_command_targets(line)
            self.set_default_targets(line)
        except ValueError, e:
            log.error(e)
            return self.no_cmd

    def set_default_targets(self, target):
        self._default_targets = target
        self.update_prompt()

    def _try_set_command_targets(self, target):
        if target:
            # found some target, check if it exists
            workers = self.orc.search_targets(target)
            if workers:
                self._command_targets = target
            else:
                raise ValueError('Cannot find target workers: %s' % target)

    def postcmd(self, stop, line):
        self._command_targets = None
        return cmd.Cmd.postcmd(self, stop, line)

    def do_quit(self, args):
        pt.disable_auto_restart()
        self.orc.stop()

    def do_discovery(self, args=None):
        self.orc.perform_discovery()
        self.do_list()

    def print_status(self, request_state):
        def extract_status(output, code):
            if code == 0:
                lines = output.splitlines()
                status = 'UNKNOWN'
                status_line = None
                for line in lines:
                    if 'STATE' in line:
                        status_line = line
                        break
                if status_line:
                    status = status_line.split(':')[-1].strip()
                return status
            else:
                return 'ERROR %d: %s' % (code, output)

        statuses = [[details.response.name, extract_status(details.response.output, details.response.result)]
                    for details in request_state.get_response_details()]
        print tabulate(statuses, headers=['Name', 'Status'])
        if not request_state.is_responded:
            not_responded = [[self.orc.get_worker(), '*** ERROR: NO ANSWER ***'] for target in
                             request_state.not_responded()]
            print '\nNot answered:'
            print tabulate(statuses, headers=['Name', 'Status'])

    def do_status(self, args=None):
        self.execute_script('mt4_status', self.print_status)

    def execute_script(self, script, callback=None):
        try:
            targets = self.orc.search_targets(self._command_targets)
            state = self.orc.send_execute_request(script, targets, callback)
            state.wait_for_responses()
        except Exception, e:
            log.error(e)

    def do_start(self, args=None):
        self.execute_script('mt4_start')

    def do_stop(self, args=None):
        self.execute_script('mt4_stop')

    def do_clean(self, args=None):
        self.execute_script('mt4_clean_logs')

    def do_init(self, args=None):
        self.execute_script('mt4_clean_bases')

    def do_script(self, args=None):
        if not args[0]:
            log.error('Specify script name as parameter')
            return
        args = args[0]
        self.execute_script(args[0])

    def do_list(self, args=None):
        print 'Discovered: '
        workers = self.orc.get_workers()
        self.print_workers(workers)

    def do_update(self, args=None):
        self.execute_script('update_src')

    def do_restart(self, args=None):
        try:
            targets = self.orc.search_targets(self._command_targets)
            state = self.orc.restart_targets(targets, 'Manual')
            wait_for_restart = 2
            print 'Waiting %d seconds for worker to restart...' % wait_for_restart
            time.sleep(wait_for_restart)
            self.do_discovery()
        except Exception, e:
            log.error(e)

    def do_verbose(self, args=None):
        if str(args).lower() == 'off':
            self.orc.verbose = False
        else:
            self.orc.verbose = True
        print 'Verbose mode: %s' % self.orc.verbose

    def start(self):
        cmd.Cmd.cmdloop(self, 'Orchestrator terminal')

    @staticmethod
    def print_workers(workers):
        sorted_list = sorted(workers, key=lambda w: (w.group, w.ip))
        table = [[worker.name, worker.ip, worker.group, worker.uuid] for worker in sorted_list]
        print tabulate(table, headers=['Name', 'IP', 'Group', 'UUID'])


class Orchestrator(object):
    def __init__(self):
        self.verbose = False
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
        self.__threads.add(self._terminal.start)

        log.debug('Own UUID: %s', self.info.uuid)

    def processor(self, response, properties):
        if isinstance(response, pt.protocol.Response):
            request_id = properties.correlation_id
            if request_id:
                request_state = self._states[request_id]
                request_state.collect_response(response, properties)

            else:
                # probably only case is greeting discovery response set as 'Hello'
                if isinstance(response, pt.DiscoveryResponse):
                    self._workers.append(response)
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

    def on_discovery_collect(self, response, properties):
        del properties
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

    def search_targets(self, query='*'):
        targets = None
        if query:
            search_by_group = self._workers.find(group=query)
            search_by_name = self._workers.find(name=query)
            search_by_uuid = self._workers.find(uuid=query)
            search_by_ip = self._workers.find(ip=query)
            if query == '*':
                targets = [worker.uuid for worker in self._workers]
            if search_by_group:
                targets = [worker.uuid for worker in search_by_group]
            elif search_by_name:
                targets = [worker.uuid for worker in search_by_name]
            elif search_by_ip:
                targets = [worker.uuid for worker in search_by_name]
            elif search_by_uuid:
                targets = [worker.uuid for worker in search_by_name]
        return targets

    def get_workers(self):
        return iter(self._workers)
