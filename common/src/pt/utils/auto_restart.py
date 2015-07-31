__author__ = 'Danylo Bilyk'

import atexit
import os
import sys
import time

from logger import log


class AutoRestart(object):
    __allow_program_exit = False
    __handler_registered = False

    @staticmethod
    def perform_restart():
        python = sys.executable
        os.execl(python, python, *sys.argv)

    @staticmethod
    def enable(time_before_restart=60):
        def exit_handler():
            if AutoRestart.__allow_program_exit:
                log.info('Program is stopped.')
                return
            log.info('Program is about auto-restart in %d seconds...', time_before_restart)
            time.sleep(time_before_restart)
            log.debug('Initiating restart.')
            AutoRestart.perform_restart()

        if not AutoRestart.__handler_registered:
            atexit.register(exit_handler)
            AutoRestart.__handler_registered = True

    @staticmethod
    def disable():
        AutoRestart.__allow_program_exit = True
