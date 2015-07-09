__author__ = 'Danylo Bilyk'

import ConfigParser
import os

from logger import log

DEFAULT_CONFIG = 'config.ini'
MAIN_SECTION = 'main'
CONNECTION_SECTION = 'connection'
EXCHANGE_SECTION = 'exchange'


def reload(filename=DEFAULT_CONFIG):
    _parser.read(filename)


def get(option, section=MAIN_SECTION):
    value = None
    try:
        value = _parser.get(section, option, vars=os.environ)
        log.debug('config.%s.%s=%s', section, option, value)
    except ConfigParser.NoOptionError as e:
        log.error('No option %s found', option)
    except ConfigParser.NoSectionError as e:
        log.error('No section %s found', section)
    return value


def set(option, value, section=MAIN_SECTION):
    pass


def get_options(section):
    options = dict(_parser.items(section))
    return {k: get(k, section) for k in options.keys()}


_parser = ConfigParser.ConfigParser()
reload()
