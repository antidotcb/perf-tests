__author__ = 'Danylo Bilyk'

from pt import RabbitConnection

from pt.protocol import Listener, Sender
from pt.processors import RequestProcessor
from pt.utils import Config

if __name__ == '__main__':
    config = Config()

    options = Config().get_options(Config.CONNECTION_SECTION)
    connection_options = Config().get_options(Config.CONNECTION_SECTION)
    exchanges = Config().get_options(Config.EXCHANGE_SECTION)

    connection = RabbitConnection(connection_options)
    in_exchange = exchanges['request']
    out_exchange = exchanges['report']

    response_sender = Sender(connection, out_exchange)
    request_listener = Listener(connection, in_exchange, RequestProcessor(response_sender).process)
    request_listener.start()

    connection.close()
