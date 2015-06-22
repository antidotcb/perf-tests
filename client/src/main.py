__author__ = 'Danylo Bilyk'
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()


channel.exchange_declare(exchange='fan-out',
                         type='fanout')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='fan-out',
                   queue=queue_name)

def callback(channel, method, properties, body):
    print " [x] body: %r" % (body)
    print " [-] channel: ", (channel)
    print " [-] method: ", (method)
    print " [-] properties: ", (properties)
    print ""

channel.basic_consume(callback,
                  queue=queue_name,
                  no_ack=True)

print ' [*] Waiting for requests. To exit press CTRL+C'
channel.start_consuming()
