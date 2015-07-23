__author__ = 'Danylo Bilyk'

from optparse import OptionParser
import os
import uuid
import platform
import socket
import atexit
from ConfigParser import ConfigParser, NoOptionError, NoSectionError

from .utils import disable_auto_restart
from .logger import set_log_level

_MAIN_SECTION = 'main'


class Config(object):
    _parser = ConfigParser()

    DEFAULT_CONFIG = '..\\config.ini'
    __CONNECTION_SECTION = 'connection'
    __EXCHANGE_SECTION = 'exchange'

    __UUID_OPTION = 'uuid'
    __IP_OPTION = 'ip'
    __NAME_OPTION = 'name'
    __GROUP_OPTION = 'group'

    def __init__(self):
        raise NotImplemented('Only static class usage allowed.')

    @staticmethod
    def load(filename=DEFAULT_CONFIG):
        Config._parser.read(filename)

    @staticmethod
    def get_option(option, section=_MAIN_SECTION):
        value = None
        try:
            value = Config._parser.get(section, option, vars=os.environ)
        except (NoOptionError, NoSectionError):
            pass
        return value

    @staticmethod
    def get_options(section):
        options = dict(Config._parser.items(section))
        options = {k: Config.get_option(k, section) for k in options.keys()}
        return options

    @staticmethod
    def exchanges():
        return Config.get_options(Config.__EXCHANGE_SECTION)

    @staticmethod
    def connection():
        return Config.get_options(Config.__CONNECTION_SECTION)

    @staticmethod
    def __set_option(option, value, section=_MAIN_SECTION):
        if section not in Config._parser.sections():
            Config._parser.add_section(section)

        if value:
            Config._parser.set(section, option, value)
        else:
            try:
                if Config._parser.get(section, option, value):
                    Config._parser.remove_option(section, option)
            except NoOptionError:
                # no need to do removal - option does not exist
                pass

    @staticmethod
    def set_group(group):
        Config.__set_option(Config.__GROUP_OPTION, group)

    @staticmethod
    def set_uuid(_uuid):
        Config.__set_option(Config.__UUID_OPTION, _uuid)

    @staticmethod
    def set_name(name):
        Config.__set_option(Config.__NAME_OPTION, name)

    @staticmethod
    def set_ip(ip):
        Config.__set_option(Config.__IP_OPTION, ip)

    @staticmethod
    def configure():
        _uuid = str(uuid.uuid4())
        ip = socket.gethostbyname(socket.gethostname())

        Config.set_uuid(_uuid)
        Config.set_name(platform.node())
        Config.set_ip(ip)

        parser = OptionParser()
        parser.add_option("--group", dest="group", help="specify a group for worker", metavar="GROUP")
        options, args = parser.parse_args()
        if options.group:
            Config.set_group(options.group)

        if not Config.get_option('group'):
            disable_auto_restart()
            raise EnvironmentError('You should specify group in config.ini or in parameter --group')

    @staticmethod
    def save_config(filename=DEFAULT_CONFIG):
        # cleanup not permanent values
        Config.set_uuid(None)
        Config.set_ip(None)
        Config.set_name(None)

        cfg_file = open(filename, 'w')
        Config._parser.write(cfg_file)
        cfg_file.close()

    @staticmethod
    def get_log_level():
        level = Config.get_option('log_level')
        if not level:
            level = 'DEBUG'
        return level

    @staticmethod
    def init(filename):
        Config.load(filename)
        Config.configure()
        set_log_level(Config.get_log_level())
        atexit.register(Config.save_config)


Config.init(Config.DEFAULT_CONFIG)
