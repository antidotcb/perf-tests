__author__ = 'Danylo Bilyk'

from pt import RabbitConnection
from pt.protocol import Listener
from pt.processors import RequestProcessor
from pt.utils import Config

if __name__ == '__main__':
    config = Config()

    options = Config().get_options(Config.CONNECTION_SECTION)
    connection_options = Config().get_options(Config.CONNECTION_SECTION)
    exchanges = Config().get_options(Config.EXCHANGE_SECTION)

    connection = RabbitConnection(connection_options)
    exchange = exchanges['request']
    client = Listener(connection, exchange, RequestProcessor())
    client.start()
