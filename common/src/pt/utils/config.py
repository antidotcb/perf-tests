__author__ = 'Danylo Bilyk'

import ConfigParser
import os
import uuid
import platform
import socket
import atexit
from argparse import ArgumentParser

from logger import log

DEFAULT_CONFIG = '..\\config.ini'
MAIN_SECTION = 'main'
CONNECTION_SECTION = 'connection'
EXCHANGE_SECTION = 'exchange'


def update(filename=DEFAULT_CONFIG):
    __parser.read(filename)


def get(option, section=MAIN_SECTION):
    value = None
    try:
        value = __parser.get(section, option, vars=os.environ)
    except ConfigParser.NoOptionError, e:
        log.error('No option %s found. Exception: %s', option, e)
    except ConfigParser.NoSectionError, e:
        log.error('No section %s found. Exception: %s', section, e)
    return value


def get_options(section):
    options = dict(__parser.items(section))
    options = {k: get(k, section) for k in options.keys()}
    log.debug(options)
    return options


def exchanges():
    return get_options(EXCHANGE_SECTION)


def connection():
    return get_options(CONNECTION_SECTION)


def set_group(group):
    __parser.set(MAIN_SECTION, 'group', group)


def set_uuid(uuid):
    __parser.set(MAIN_SECTION, 'uuid', uuid)


def set_name(name):
    __parser.set(MAIN_SECTION, 'name', name)


def set_ip(ip):
    __parser.set(MAIN_SECTION, 'ip', ip)


def __set_defaults():
    if MAIN_SECTION not in __parser.sections():
        __parser.add_section(MAIN_SECTION)

    if not get('uuid'):
        _uuid = str(uuid.uuid4())
        set_uuid(_uuid)
    if not get('name'):
        set_name(platform.node())
    if not get('group'):
        parser = ArgumentParser()
        parser.add_argument("--group", dest="group", required=True, help="specify a group for worker", metavar="GROUP")
        args = parser.parse_args()
        group = args.group
        set_group(group)
    if not get('ip'):
        ip = socket.gethostbyname(socket.gethostname())
        set_ip(ip)


def save_config(filename=DEFAULT_CONFIG):
    cfg_file = open(filename, 'w')
    __parser.write(cfg_file)
    cfg_file.close()


__parser = ConfigParser.ConfigParser()
update()
__set_defaults()
atexit.register(save_config)
