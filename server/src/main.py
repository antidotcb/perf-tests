__author__ = 'Danylo Bilyk'

import pika
from pt import MessageSender
from pt.request import DiscoveryRequest
from pt.utils.protocol import Protocol
from bson import json_util

print Protocol().list()

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

sender = MessageSender(connection)

dr = DiscoveryRequest()
json = dr.to_json()
parsed = dict(json_util.loads(json))
print Protocol().create(parsed).to_json()

channel.exchange_declare(exchange='fan-out',
                         type='fanout')
sender.send(dr)

#connection.close()

if __name__ == '__main__':
    print 'Orchestrator server', __package__