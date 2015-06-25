__author__ = 'Danylo Bilyk'

from config import Config
from listener import Listener
from pt.request import DiscoveryRequest
from pt.utils.protocol import Protocol

print Protocol().list()

if __name__ == '__main__':
    config = Config(Config.DEFAULT_CONFIG)
    client = Listener(config)
    client.run()
