__author__ = 'Danylo Bilyk'

from pt.message import JsonMessage


class DiscoveryRequest(JsonMessage):
    DEFAULTS = {
        'message': 'Default message'
    }

    def __init__(self, *args, **kwargs):
        super(DiscoveryRequest, self).__init__(*args, **kwargs)
        pass
