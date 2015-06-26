__author__ = 'Danylo Bilyk'

import pika

from utils import Singleton


class RabbitConnection:
    __metaclass__ = Singleton

    def __init__(self, options):
        if not isinstance(options, dict):
            raise TypeError('Options should be a dictionary')
        self._options = self._prepare_options(options)
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(**self._options))
        self.channel = self._connection.channel()

    def create_exchange(self, exchange, exchange_type, *args, **kwargs):
        return self.channel.exchange_declare(exchange=exchange, type=exchange_type, passive=False, **kwargs)

    def get_exchange(self, exchange, **kwargs):
        passive = 'passive'
        if passive in kwargs.keys():
            logger.warning('`%s` argument is ignored by this function' % passive)
            del kwargs[passive]
        return self.channel.exchange_declare(exchange=exchange, passive=True, **kwargs)

    @staticmethod
    def _prepare_options(options):
        # replace login & password with pika credentials
        if 'login' in options.keys():
            pwd = None
            if 'password' in options.keys():
                pwd = options['password']
            login = options['login']
            del options['login']
            del options['password']
            options['credentials'] = pika.PlainCredentials(login, pwd)
        return options

    def close(self):
        self._connection.close()
