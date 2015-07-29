__author__ = 'Danylo Bilyk'

import logging
import sys

log = logging.getLogger('pt')
__formatter = logging.Formatter('%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s')
__ch = logging.StreamHandler(sys.stdout)
__ch.setFormatter(__formatter)
log.addHandler(__ch)


def update_log_level(level):
    log.setLevel(level)


update_log_level(logging.DEBUG)
