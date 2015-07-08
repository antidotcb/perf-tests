__author__ = 'Danylo Bilyk'

import sys
import time

import pika

from pt.scenarios import restart


def callback(*args, **kwargs):
    print args
    print kwargs


class ExitState(object):
    def __init__(self):
        self.restart = True
        self.seconds2wait = 30


exitState = ExitState()


class Terminal(object):
    def __init__(self):
        _connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self._channel = _connection.channel()
        self._channel.exchange_declare(exchange='test', type='direct', passive=False)

        _queue = self._channel.queue_declare(exclusive=True)
        _queue_name = _queue.method.queue

        self._channel.queue_bind(exchange='test', queue=_queue_name)

        self._channel.basic_consume(callback, queue=_queue_name)

    def run(self):
        try:
            self._channel.start_consuming()
        except Exception, e:
            print sys.stderr, e
            raise


if __name__ == '__main__':
    try:
        terminal = Terminal()
        terminal.run()
    except Exception, e:
        print >> sys.stderr, e


def exit_handler(exit_state):
    time_to_restart = 60
    print >> sys.stderr, 'Program encountered a critical error'
    print 'Program is about auto-restart in %d seconds...' % time_to_restart
    time.sleep(time_to_restart)
    print 'Initiating restart.'
    restart()


import atexit

atexit.register(exit_handler, exitState)
