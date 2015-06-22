__author__ = 'Danylo Bilyk'

import pika
from pt import MessageSender
from pt.request import DiscoveryRequest

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

sender = MessageSender(connection)

dr = DiscoveryRequest()

channel.exchange_declare(exchange='fan-out',
                         type='fanout')
sender.send(dr)

connection.close()

if __name__ == '__main__':
    print 'Orchestrator server', __package__