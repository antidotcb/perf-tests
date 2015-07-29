__author__ = 'Danylo Bilyk'

import pt

from worker import Worker

if __name__ == '__main__':
    pt.enable_auto_restart()
    worker = Worker()
    worker.start()
