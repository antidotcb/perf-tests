__author__ = 'Danylo Bilyk'

import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello')

channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')
print " [x] Sent 'Hello World!'"

channel.queue_delete(queue='hello')
channel.close()

connection.close()

if __name__ == '__main__':
    print 'Orchestrator server', __package__