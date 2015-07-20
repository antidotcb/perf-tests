__author__ = 'antidotcb'

import time
import threading


def timeout_callback(timeout, callback, *args, **kwargs):
    time.sleep(timeout)
    callback(*args, **kwargs)


class ThreadCollection(object):
    def __init__(self):
        self.__threads = []

    def append(self, target, args=(), kwargs=None):
        thread = threading.Thread(target=target, args=args, kwargs=kwargs)
        self.__threads.append(thread)
        return thread

    def timeout_callback(self, callback, timeout, *args, **kwargs):
        args = (callback, timeout,) + args
        t = self.append(timeout_callback, args=args, kwargs=kwargs)
        t.start()

    def start(self):
        for t in self.__threads:
            t.start()

    def join(self):
        for t in self.__threads:
            t.join()

    def stop(self):
        for t in self.__threads:
            try:
                # noinspection PyProtectedMember
                t._Thread__stop()
            except Exception, e:
                print('%s could not be terminated. Exception: %s' % (t.getName(), e))
