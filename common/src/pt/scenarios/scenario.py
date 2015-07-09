__author__ = 'Danylo Bilyk'

import time
import threading

from pt.utils import log


class Scenario(threading.Thread):
    def __init__(self, name, *args, **kwargs):
        super(Scenario, self).__init__(target=self.run, name=name, args=args, kwargs=kwargs)
        self._status = 0

    def status(self):
        return self._status

    def _pre_run(self, *args, **kwargs):
        log.debug('%s _pre_run: (args=%s kwargs=%s' % (self.name, args, kwargs))
        log.info('Start scenario execution: %s', self.name)

    def _post_run(self, *args, **kwargs):
        log.debug('%s _post_run: (args=%s kwargs=%s)' % (self.name, args, kwargs))
        log.info('End scenario execution: %s', self.name)

    def _exec_run(self, *args, **kwargs):
        log.debug('%s _exec_run: (args=%s kwargs=%s)' % (self.name, args, kwargs))
        time.sleep(1)

    def run(self, *args, **kwargs):
        self._pre_run(*args, **kwargs)
        result = self._exec_run(*args, **kwargs)
        self._post_run(*args, **kwargs)
        return result
