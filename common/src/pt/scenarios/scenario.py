__author__ = 'Danylo Bilyk'

import time
import threading
import exceptions

from pt.utils import log


class TimeoutError(exceptions.BaseException):
    def __init__(self, *args, **kwargs):
        super(TimeoutError, self).__init__(*args, **kwargs)


class Scenario(object):
    def __init__(self, name, *args, **kwargs):
        self._thread = threading.Thread(target=self.run, name=name, args=args, kwargs=kwargs)
        self._status = 0
        self._result = None

    def status(self):
        return self._status

    def result(self):
        return self._result

    def _pre_run(self, *args, **kwargs):
        log.debug('%s _pre_run: (args=%s kwargs=%s)' % (self._thread.name, args, kwargs))
        log.info('Start scenario execution: %s', self._thread.name)

    def _post_run(self, *args, **kwargs):
        log.debug('%s _post_run: (args=%s kwargs=%s)' % (self._thread.name, args, kwargs))
        log.info('End scenario execution: %s', self._thread.name)

    def _exec_run(self, *args, **kwargs):
        log.debug('%s _exec_run: (args=%s kwargs=%s)' % (self._thread.name, args, kwargs))
        time.sleep(1)

    def run(self, *args, **kwargs):
        self._result = self._exec_run(*args, **kwargs)

    def start(self, timeout, *args, **kwargs):
        self._pre_run(*args, **kwargs)
        self._thread.start()
        self._thread.join(timeout)
        if self._thread.isAlive():
            raise TimeoutError('Timeout expired during running script %s', self._thread.name)
        else:
            self._post_run(*args, **kwargs)
