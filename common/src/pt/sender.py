__author__ = 'Danylo Bilyk'

from .utils.json_message import JsonMessage

class MessageSender:
    def __init__(self, connection):
        self._channel = connection.channel()

    def send(self, message):
        if isinstance(message, JsonMessage):
            json = message.to_json()
            self._channel.basic_publish(exchange='fan-out', routing_key='', body=json)
        else:
            raise TypeError("Unsupported message type")
