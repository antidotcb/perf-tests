__author__ = 'Danylo Bilyk'

import pika

from pt.utils import Configuration, log


def fix_credentials(_dict):
    login = Configuration.LOGIN_OPTION
    password = Configuration.PASSWORD_OPTION
    credentials = Connection.__CREDENTIALS_ARGUMENT__

    login_value, password_value = None, None
    if login in _dict.keys():
        login_value = _dict[login]
        del _dict[login]
    if password in _dict.keys():
        password_value = _dict[password]
        del _dict[password]
    if password_value or login:
        _dict[credentials] = pika.PlainCredentials(login_value, password_value)

    return _dict


def clean_passive(_dict):
    passive = Connection.__PASSIVE_ARGUMENT__
    if passive in _dict.keys():
        log.warning('`%s` argument is ignored by this function' % passive)
        del _dict[passive]
    return _dict


class Connection(object):
    __CREDENTIALS_ARGUMENT__ = 'credentials'
    __PASSIVE_ARGUMENT__ = 'passive'

    def __init__(self, **kwargs):
        self._conn = pika.BlockingConnection(pika.ConnectionParameters(**fix_credentials(kwargs)))

    def new_channel(self, channel_number=None):
        return self._conn.channel(channel_number)

    def create_exchange(self, name, exchange_type, **kwargs):
        channel = self.new_channel()
        exchange = channel.exchange_declare(exchange=name, exchange_type=exchange_type, **clean_passive(kwargs))
        channel.close()
        return exchange

    def close(self):
        self._conn.close()
