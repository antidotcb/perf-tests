__author__ = 'Danylo Bilyk'

class SimpleProcessor:
    def __init__(self):
        pass

    def process(self, channel, method, properties, body):
        logger.debug(' [+] body: %r', body)
        logger.debug(' [-] channel: %r', channel)
        logger.debug(' [-] method: %r', method)
        logger.debug(' [-] properties: %r', properties)
        try:
            if self._processor:
                self._processor.process(channel, method, properties, body)
            parsed = dict(json_util.loads(body))
            message = self._protocol.create(dict(parsed))
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return message
        except Exception, e:
            logger.exception('Exception occured: %s', e)
        return None
