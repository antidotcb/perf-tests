__author__ = 'Danylo Bilyk'

import pika
from pt.protocol import Sender
from pt import RabbitConnection
from pt.request import DiscoveryRequest
from pt.utils import Config




if __name__ == '__main__':
    config = Config()

    options = Config().get_options(Config.CONNECTION_SECTION)
    connection_options = Config().get_options(Config.CONNECTION_SECTION)
    exchange_opts = Config().get_options(Config.EXCHANGE_SECTION)

    connection = RabbitConnection(connection_options)

    request_exchange=exchange_opts['request']

    connection.create_exchange(request_exchange, 'fanout')

    sender = Sender(connection, request_exchange)

    sender.send(DiscoveryRequest())

    connection.close()