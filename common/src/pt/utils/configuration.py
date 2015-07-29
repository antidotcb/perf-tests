__author__ = 'Danylo Bilyk'

import os
import platform
import socket
import uuid
from optparse import OptionParser
from ConfigParser import ConfigParser, NoOptionError, NoSectionError

from logger import update_log_level


class Configuration(object):
    GLOBAL_CONFIG = os.path.join(os.getcwd(), '..', 'config.ini')
    LOCAL_CONFIG = os.path.join(os.getcwd(), 'config.ini')

    __EXCHANGE_SECTION__ = 'EXCHANGES'
    __CONNECTION_SECTION__ = 'CONNECTION'
    __GENERAL_SECTION__ = 'GENERAL'

    UUID_OPTION = 'uuid'
    IP_OPTION = 'ip'
    NAME_OPTION = 'name'
    GROUP_OPTION = 'group'
    LOG_LEVEL_OPTION = 'log_level'

    HOST_OPTION = 'host'
    VIRTUAL_HOST_OPTION = 'virtual_host'
    LOGIN_OPTION = 'login'
    PASSWORD_OPTION = 'password'

    __CONNECTION_OPTIONS__ = {HOST_OPTION, VIRTUAL_HOST_OPTION, LOGIN_OPTION, PASSWORD_OPTION}

    DEFAULTS = {
        NAME_OPTION: platform.node(),
        IP_OPTION: socket.gethostbyname(socket.gethostname()),
        UUID_OPTION: str(uuid.uuid4()),
        GROUP_OPTION: "undefined",
        LOG_LEVEL_OPTION: "DEBUG",
        HOST_OPTION: "localhost",
        VIRTUAL_HOST_OPTION: "/",
        LOGIN_OPTION: "guest",
        PASSWORD_OPTION: "guest"
    }

    def __init__(self):
        global_config = self._load(self.GLOBAL_CONFIG)
        self._parser = self._load(self.LOCAL_CONFIG, defaults=global_config)
        self.__parse_cmd_line()
        update_log_level(self.get_log_level())

    def get_option(self, option, section=__GENERAL_SECTION__):
        try:
            value = self._parser.get(section, option, vars=os.environ)
        except (NoOptionError, NoSectionError):
            return None
        return value

    def get_options(self, section):
        options = dict(self._parser.items(section))
        options = {k: self.get_option(k, section) for k in options.keys()}
        return options

    def save(self):
        self.__clean_temporary_values()

        cfg_file = open(self.LOCAL_CONFIG, 'w')
        self._parser.write(cfg_file)
        cfg_file.close()

    def get_log_level(self):
        level = self.get_option(self.LOG_LEVEL_OPTION)
        if not level:
            level = self.DEFAULTS[self.LOG_LEVEL_OPTION]
        return level

    def group(self):
        return self.get_option(self.GROUP_OPTION)

    def uuid(self):
        return self.get_option(self.UUID_OPTION)

    def name(self):
        return self.get_option(self.NAME_OPTION)

    def ip(self):
        return self.get_option(self.IP_OPTION)

    def update_group(self, group):
        self.__set_option(self.GROUP_OPTION, group, self.__GENERAL_SECTION__)

    def update_name(self, name):
        self.__set_option(self.NAME_OPTION, name, self.__GENERAL_SECTION__)

    def exchanges(self):
        return self.get_options(self.__EXCHANGE_SECTION__)

    def connection(self):
        return self.get_options(self.__CONNECTION_SECTION__)

    def __set_option(self, option, value, section):
        if section not in self._parser.sections():
            self._parser.add_section(section)

        if value:
            self._parser.set(section, option, value)
        else:
            try:
                if self._parser.get(section, option):
                    self._parser.remove_option(section, option)
            except (NoOptionError, NoSectionError):
                pass

    def __clean_temporary_values(self):
        self.__set_option(self.UUID_OPTION, None, self.__GENERAL_SECTION__)
        self.__set_option(self.IP_OPTION, None, self.__GENERAL_SECTION__)

    def __parse_cmd_line(self):
        parser = OptionParser()
        for option in self.DEFAULTS.keys():
            parser.add_option(("--" + option), dest=option)
        options, args = parser.parse_args()

        for option in options.__dict__:
            value = options.__dict__[option]

            section = self.__GENERAL_SECTION__
            if option in self.__CONNECTION_OPTIONS__:
                section = self.__CONNECTION_SECTION__

            if value:
                self.__set_option(option, value, section)
            else:
                if not self.get_option(option, section):
                    default = self.DEFAULTS[option]
                    self.__set_option(option, default, section)

    @staticmethod
    def _load(filename, defaults=None):
        parser = ConfigParser()
        parser.read(filename)
        if defaults:
            for section in defaults.sections():
                for option, value in defaults.items(section):
                    if section not in parser.sections():
                        parser.add_section(section)
                    parser.set(section, option, value)
        return parser

config = Configuration()
