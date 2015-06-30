__author__ = 'Danylo Bilyk'

import time

import gevent

from pt.utils import logger


class Scenario(object):
    def __init__(self, name, timeout=None):
        self.name = name
        self.timeout = timeout
        self.__job = None
        self.__ready = False
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

    def execute(self, *args, **kwargs):
        self._pre_run(*args, **kwargs)
        self._exec_run(*args, **kwargs)
        self._post_run(*args, **kwargs)
        self.__ready = True

    def start(self, *args, **kwargs):
        self.__job = gevent.spawn(self.execute, *args, **kwargs)
        return self.__job

    def wait(self, timeout=None):
        if timeout:
            self.timeout = timeout
        if self.__job:
            gevent.joinall([self.__job], self.timeout)

    def stop(self):
        gevent.kill(self.__job)

    def ready(self):
        return self.__job.dead
