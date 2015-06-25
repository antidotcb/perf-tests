__author__ = 'Danylo Bilyk'

from pt import RabbitConnection, Config
from pt.client import Listener

if __name__ == '__main__':
    config = Config()

    options = Config().get_options(Config.CONNECTION_SECTION)
    connection_options = Config().get_options(Config.CONNECTION_SECTION)
    exchanges = Config().get_options(Config.EXCHANGE_SECTION)

    connection = RabbitConnection(connection_options)

    client = Listener(exchanges['request'], None)
    client.run()
