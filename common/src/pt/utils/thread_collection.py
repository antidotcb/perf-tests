__author__ = 'Danylo Bilyk'

import time
import threading


def timeout_callback(timeout, callback):
    time.sleep(timeout)
    callback()


class ThreadCollection(object):
    def __init__(self):
        self.__threads = []

    def add(self, callback):
        thread = threading.Thread(target=callback)
        self.__threads.append(thread)
        return thread

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
