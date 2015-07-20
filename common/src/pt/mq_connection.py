__author__ = 'Danylo Bilyk'

import pika

from pt.utils import log


def fix_credentials(_dict):
    login, pwd = None, None
    if 'login' in _dict.keys():
        login = _dict['login']
        del _dict['login']
    if 'password' in _dict.keys():
        pwd = _dict['password']
        del _dict['password']
    if pwd or login:
        _dict['credentials'] = pika.PlainCredentials(login, pwd)
    return _dict


def clean_passive(_dict):
    passive = 'passive'
    if passive in _dict.keys():
        log.warning('`%s` argument is ignored by this function' % passive)
        del _dict[passive]
    return _dict


class Connection(object):
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
