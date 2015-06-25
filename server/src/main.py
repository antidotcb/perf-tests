__author__ = 'Danylo Bilyk'

import pika
from pt.server import Sender
from pt import Config, RabbitConnection
from pt.request import DiscoveryRequest




if __name__ == '__main__':
    config = Config()

    options = Config().get_options(Config.CONNECTION_SECTION)
    connection_options = Config().get_options(Config.CONNECTION_SECTION)
    exchange_opts = Config().get_options(Config.EXCHANGE_SECTION)

    connection = RabbitConnection(connection_options)


    request_exchange=exchange_opts['request']

    connection.exchange_declare(exchange=request_exchange, type='fanout')

    connection_opts = get_connection_options()
    connection = pika.BlockingConnection(pika.ConnectionParameters(**connection_opts))
    channel = connection.channel()





    sender = Sender(connection, request_exchange)

    sender.send(DiscoveryRequest())

    connection.close()