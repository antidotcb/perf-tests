__author__ = 'Danylo Bilyk'

import logging
import sys

log = logging.getLogger('pt')
log.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s')
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(formatter)
log.addHandler(ch)


def set_log_level(level):
    log.setLevel(level)
