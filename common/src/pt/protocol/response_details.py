__author__ = 'Danylo Bilyk'


class ResponseDetails(object):
    def __init__(self, response, properties):
        self.sender = properties.correlation_id
        self.response = response
        self.properties = properties
