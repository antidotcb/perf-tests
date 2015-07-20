__author__ = 'Danylo Bilyk'

import ConfigParser
import os

from logger import log

DEFAULT_CONFIG = '..\\config.ini'
MAIN_SECTION = 'main'
CONNECTION_SECTION = 'connection'
EXCHANGE_SECTION = 'exchange'


def update(filename=DEFAULT_CONFIG):
    _parser.read(filename)


def get(option, section=MAIN_SECTION):
    value = None
    try:
        value = _parser.get(section, option, vars=os.environ)
        log.debug('config.%s.%s=%s', section, option, value)
    except ConfigParser.NoOptionError, e:
        log.error('No option %s found. Exception: %s', option, e)
    except ConfigParser.NoSectionError, e:
        log.error('No section %s found. Exception: %s', section, e)
    return value


def get_options(section):
    options = dict(_parser.items(section))
    return {k: get(k, section) for k in options.keys()}


def exchanges():
    return get_options(EXCHANGE_SECTION)


def connection():
    return get_options(CONNECTION_SECTION)


_parser = ConfigParser.ConfigParser()
update()
