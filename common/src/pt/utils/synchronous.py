__author__ = 'Danylo Bilyk'

from functools import wraps


def synchronous(lock_name):
    def _synchronous(func):
        @wraps(func)
        def ___synchronous(self, *args, **kwargs):
            locker = self.__getattribute__(lock_name)
            locker.acquire()
            try:
                return func(self, *args, **kwargs)
            finally:
                locker.release()

        return ___synchronous

    return _synchronous
