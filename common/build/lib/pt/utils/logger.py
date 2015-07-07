__author__ = 'Danylo Bilyk'

import logging
import sys

pt_logger = logging.getLogger('pt')
pt_logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
pt_logger.addHandler(ch)


def debug(msg, *args, **kwargs):
    pt_logger.debug(msg, *args, **kwargs)


def warn(msg, *args, **kwargs):
    pt_logger.warn(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    pt_logger.info(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    pt_logger.error(msg, *args, **kwargs)


def exception(msg, *args, **kwargs):
    pt_logger.exception(msg, *args, **kwargs)
