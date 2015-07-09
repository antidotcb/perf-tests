__author__ = 'Danylo Bilyk'

import sys
import time

import pt
from pt.scenarios import restart


class Terminal(object):
    def __init__(self):
        pass

    def run(self):
        pass


if __name__ == '__main__':
    terminal = Terminal()
    terminal.run()



def exit_handler():
    time_to_restart = 60
    print 'Program is about auto-restart in %d seconds...' % time_to_restart
    time.sleep(time_to_restart)
    print 'Initiating restart.'
    restart()


import atexit

atexit.register(exit_handler)
