__author__ = 'Danylo Bilyk'
import pika
from pt import scenario
from pt.request.discovery import DiscoveryRequest

s1 = scenario('test')
s1.run()

dr = DiscoveryRequest()
print dr.to_json()
'''
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello')

def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)

channel.basic_consume(callback,
                  queue='hello',
                  no_ack=True)

print ' [*] Waiting for requests. To exit press CTRL+C'
channel.start_consuming()
'''