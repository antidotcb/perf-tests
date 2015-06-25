__author__ = 'Danylo Bilyk'

from pt.utils.json_message import JsonMessage


class DiscoveryRequest(JsonMessage):

    _FIELDS = {
        'message': 'Default message'
    }

    def __init__(self, *args, **kwargs):
        super(DiscoveryRequest, self).__init__(*args, **kwargs)
        pass
