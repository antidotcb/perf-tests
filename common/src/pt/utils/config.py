__author__ = 'Danylo Bilyk'

from optparse import OptionParser
import os
import uuid
import platform
import socket
import atexit
import ConfigParser

from logger import log
from utils import disable_auto_restart

DEFAULT_CONFIG = '..\\config.ini'
MAIN_SECTION = 'main'
CONNECTION_SECTION = 'connection'
EXCHANGE_SECTION = 'exchange'

UUID_OPTION = 'uuid'
IP_OPTION = 'ip'
NAME_OPTION = 'name'
GROUP_OPTION = 'group'


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


def __set_option(option, value, section=MAIN_SECTION):
    if section not in __parser.sections():
        __parser.add_section(section)

    if value:
        __parser.set(section, option, value)
    else:
        try:
            if __parser.get(section, option, value):
                __parser.remove_option(section, option)
        except ConfigParser.NoOptionError:
            # no need to do removal - option does not exist
            pass


def set_group(group):
    __set_option(GROUP_OPTION, group)


def set_uuid(_uuid):
    __set_option(UUID_OPTION, _uuid)


def set_name(name):
    __set_option(NAME_OPTION, name)


def set_ip(ip):
    __set_option(IP_OPTION, ip)


def __set_defaults():
    _uuid = str(uuid.uuid4())
    ip = socket.gethostbyname(socket.gethostname())

    set_uuid(_uuid)
    set_name(platform.node())
    set_ip(ip)

    parser = OptionParser()
    parser.add_option("--group", dest="group", help="specify a group for worker", metavar="GROUP")
    options, args = parser.parse_args()
    if options.group:
        set_group(options.group)

    if not get('group'):
        disable_auto_restart()
        raise EnvironmentError('You should specify group in config.ini or in parameter --group')


def __cleanup_exceptions():
    set_uuid(None)
    set_ip(None)
    set_name(None)


def save_config(filename=DEFAULT_CONFIG):
    __cleanup_exceptions()
    cfg_file = open(filename, 'w')
    __parser.write(cfg_file)
    cfg_file.close()


__parser = ConfigParser.ConfigParser()
update()
__set_defaults()
atexit.register(save_config)
