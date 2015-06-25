__author__ = 'antidotcb'

import ConfigParser
import os


class Config:
    DEFAULT_CONFIG = './config.ini'
    DEFAULT_SECTION = 'main'
    server_cfg = 'server'

    def __init__(self, filename):
        self._parser = ConfigParser.ConfigParser(os.environ)
        self.update(filename)

    def update(self, filename):
        self._parser.read(filename)
        self._server = self.get(self.server_cfg)

    def server(self):
        return self._server

    def get(self, option):
        return self._parser.get(self.DEFAULT_SECTION, option)