__author__ = 'Danylo Bilyk'

import pika



def init(options):
    global _connection, channel
    if not isinstance(options, dict):
        raise TypeError('Options should be a dictionary')
    _options = _prepare_options(options)
    _connection = pika.BlockingConnection(pika.ConnectionParameters(**_options))
    channel = _connection.channel()

def create_exchange(exchange, exchange_type, **kwargs):
    return channel.exchange_declare(exchange=exchange, type=exchange_type, passive=False, **kwargs)

def get_exchange(exchange, **kwargs):
    passive = 'passive'
    if passive in kwargs.keys():
        log.warning('`%s` argument is ignored by this function' % passive)
        del kwargs[passive]
    return channel.exchange_declare(exchange=exchange, passive=True, **kwargs)

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

def close():
    _connection.close()
