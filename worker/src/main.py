__author__ = 'Danylo Bilyk'

import pt

from worker import Worker

if __name__ == '__main__':
    pt.AutoRestart.enable()
    worker = Worker()
    worker.run()
