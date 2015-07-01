__author__ = 'Danylo Bilyk'

import time
import threading

from pt.utils import logger


class Scenario(threading.Thread):
    def __init__(self, name, *args, **kwargs):
        super(Scenario, self).__init__(target=self.execute, name=name, args=args, kwargs=kwargs)
        self._status = 0

    def status(self):
        return self._status

    def _pre_run(self, *args, **kwargs):
        logger.debug('%s _pre_run: (args=%s kwargs=%s' % (self.name, args, kwargs))
        logger.info('Start scenario execution: %s', self.name)

    def _post_run(self, *args, **kwargs):
        logger.debug('%s _post_run: (args=%s kwargs=%s' % (self.name, args, kwargs))
        logger.info('End scenario execution: %s', self.name)

    def _exec_run(self, *args, **kwargs):
        logger.debug('%s _exec_run: (args=%s kwargs=%s' % (self.name, args, kwargs))
        time.sleep(1)

    def run(self):
        self._pre_run(*args, **kwargs)
        self._exec_run(*args, **kwargs)
        self._post_run(*args, **kwargs)