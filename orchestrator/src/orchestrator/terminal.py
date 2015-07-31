import cmd
import time

from tabulate import tabulate

from pt import log
import pt

__author__ = 'Danylo Bilyk'


# noinspection PyClassicStyleClass,PyUnusedLocal
class Terminal(cmd.Cmd):
    no_cmd = ''

    def __init__(self, orc):
        cmd.Cmd.__init__(self)
        self.orc = orc
        self._default_targets = '*'
        self._command_targets = None
        self.update_prompt()
        self.test_start = None
        self.test_in_progress = False

    # commands

    def do_quit(self, args=None):
        pt.AutoRestart.disable()
        self.orc.stop()
        return True

    def do_status(self, args=None):
        self.__execute_script('status', self._print_status)

    def do_default(self, args_line=None):
        args = str(args_line).split()
        if not len(args) or not args[0].strip():
            log.error("Invalid argument count")
        else:
            try:
                target = self._validate_targets(args_line)
                self._set_default_targets(target)
            except ValueError, e:
                log.error(e)
                return self.no_cmd

    def do_start(self, args=None):
        self.__execute_script('start')

    def do_stop(self, args=None):
        self.__execute_script('stop')

    def do_clean(self, args=None):
        self.__execute_script('clean')

    def do_init(self, args=None):
        self.__execute_script('init')

    def do_script(self, args=None):
        if not args[0]:
            log.error('Specify script name as parameter')
            return
        self.__execute_script(args)

    def do_list(self, args=None):
        print 'Discovered: '
        workers = self.orc.get_workers()
        self._print_workers(workers)

    def do_update(self, args=None):
        self.__execute_script('update')

    def do_restart(self, args=None):
        try:
            targets = self.__get_targets()
            state = self.orc.restart_targets(targets, 'Manual')
            wait_for_restart = 5
            print 'Waiting %d seconds for worker to restart...' % wait_for_restart
            time.sleep(wait_for_restart)
        except Exception, e:
            log.error(e)

    def do_terminate(self, args=None):
        try:
            targets = self.__get_targets()
            workers = self.orc.get_workers()
            workers_list = '\n\t* '.join([workers[uuid].name for uuid in targets])
            print 'You are about to terminate following workers:\n%s' % workers_list
            print 'After termination, workers are unable to start.'
            answer = raw_input('Are you sure you want to terminate following workers?  [Y/N]')
            if answer.lower() == 'y':
                self.orc.terminate_workers(targets)
            else:
                print 'Does you wish, Sir.'
        except Exception, e:
            log.error(e)

    def do_verbose(self, args=None):
        if str(args).lower() == 'off':
            self.orc.verbose = False
        else:
            self.orc.verbose = True
        print 'Verbose mode: %s' % self.orc.verbose

    def do_backup(self, args=None):
        try:
            callback = None
            targets = self.__get_targets()
            state = self.orc.send_backup_request(targets, callback)
            # state.wait_for_responses()
        except Exception, e:
            log.error(e)

    def do_test(self, args):
        try:
            self.orc.start_test()
        except Exception, e:
            log.error(e)

    # helpers

    def start(self):
        cmd.Cmd.cmdloop(self, 'Orchestrator terminal')

    def __get_targets(self):
        return self.orc.search_workers(self._command_targets)

    def _print_status(self, request_state):
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
            workers = self.orc.get_workers()
            not_responded = [[workers[target], '*** ERROR: NO ANSWER ***'] for target in request_state.not_responded()]
            print '\nNot answered:'
            print tabulate(statuses, headers=['Name', 'Status'])

    def _set_default_targets(self, target):
        self._default_targets = target
        self.update_prompt()

    def _validate_targets(self, target):
        if target:
            # found some target, check if it exists
            workers = self.orc.search_workers(target)
            if workers:
                return target
            else:
                raise ValueError('Cannot find target workers: %s' % target)

    def __execute_script(self, script, callback=None):
        try:
            targets = self.__get_targets()
            state = self.orc.send_execute_request(script, targets, callback)
            state.wait_for_responses()
        except Exception, e:
            log.error(e)

    @staticmethod
    def _print_workers(workers):
        sorted_list = sorted(list(workers), key=lambda w: (w.group, w.ip))
        table = [[worker.name, worker.ip, worker.group, worker.uuid] for worker in sorted_list]
        print tabulate(table, headers=['Name', 'IP', 'Group', 'UUID'])

    # cmdline terminal internals

    def update_prompt(self):

        if self._default_targets:
            self.prompt = '[%s]:' % self._default_targets
        else:
            self.prompt = ':'

    def emptyline(self):
        pass  # override method to disable repeat of last command

    def precmd(self, line):
        # target can be specified at start of command line, separated from command by semicolon
        parts = line.split(':')

        args = line.split()
        target = None
        if len(parts) > 1:
            target = parts[0]
            args = parts[1:]

        try:
            self._command_targets = self._validate_targets(target)
        except ValueError, e:
            log.error(e)
            return self.no_cmd

        if not self._command_targets:
            self._command_targets = self._default_targets

        new_line = ' '.join(args)
        return new_line

    def default(self, line):
        try:
            target = self._validate_targets(line)
            self._set_default_targets(target)
        except ValueError, e:
            return cmd.Cmd.default(self, line)

    def postcmd(self, stop, line):
        self._command_targets = None
        return cmd.Cmd.postcmd(self, stop, line)
