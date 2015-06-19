__author__ = 'Danylo Bilyk'

from pt.message import JsonMessage

class DiscoveryRequest(JsonMessage):
    FIELDS = {
        '123': '5'
    }

    def __init__(self):
        super(DiscoveryRequest, self).__init__()
        pass
