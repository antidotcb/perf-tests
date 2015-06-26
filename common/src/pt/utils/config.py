__author__ = 'antidotcb'

import ConfigParser
import os

from singleton import Singleton
from pt.utils import logger


class Config:
    __metaclass__ = Singleton

    DEFAULT_CONFIG = '../config.ini'
    MAIN_SECTION = 'main'
    CONNECTION_SECTION = 'connection'
    EXCHANGE_SECTION = 'exchange'

    def __init__(self, filename=None):
        if not filename:
            filename = self.DEFAULT_CONFIG
        self._parser = ConfigParser.ConfigParser()
        self.update(filename)

    def update(self, filename):
        logger.debug('Updating config from file %s', filename)
        self._parser.read(filename)

    def get(self, option, section=None):
        if not section:
            section = self.MAIN_SECTION
        value = None
        try:
            value = self._parser.get(section, option, vars=os.environ)
            logger.debug('config.%s.%s=%s', section, option, value)
        except NoOptionError as e:
            logger.error('No option %s found', option)
        except NoSectionError as e:
            logger.error('No section %s found', section)
        return value

    def get_options(self, section):
        options = dict(self._parser.items(section))
        return {k: self.get(k, section) for k in options.keys()}
