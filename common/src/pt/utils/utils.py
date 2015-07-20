__author__ = 'Danylo Bilyk'

import atexit
import os
import sys
import time

from logger import log

allow_program_exit = False
handler_registered = False


def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)


def enable_auto_restart(time_to_restart=60):
    def exit_handler():
        global allow_program_exit

        if allow_program_exit:
            log.debug('Program is stopped.')
            return

        log.info('Program is about auto-restart in %d seconds...', time_to_restart)
        time.sleep(time_to_restart)
        log.debug('Initiating restart.')
        restart_program()

    global handler_registered
    if not handler_registered:
        atexit.register(exit_handler)
        handler_registered = True


def disable_auto_restart():
    global allow_program_exit
    allow_program_exit = True
