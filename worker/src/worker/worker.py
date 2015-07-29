__author__ = 'Danylo Bilyk'

import pt
from pt.utils import config, log


class Worker(object):
    def __init__(self):
        self.config = config

        self._connection = pt.Connection(**self.config.connection())

        exchanges = self.config.exchanges()

        self._connection.create_exchange(exchanges['broadcast'], 'fanout')
        self._connection.create_exchange(exchanges['direct'], 'direct', durable=True)

        self._broadcast = pt.protocol.Listener(self._connection, exchanges['broadcast'], self.process)
        self._direct = pt.protocol.Listener(self._connection, exchanges['direct'], self.process,
                                            routing_key=self.config.uuid())

        self._sender = pt.protocol.Sender(self._connection, exchanges['direct'])

        self.__threads = pt.ThreadCollection()
        self.__threads.add(self._broadcast.start)
        self.__threads.add(self._direct.start)

    def start(self):
        self.__threads.start()
        self.__threads.join()

    def stop(self):
        self._direct.stop()
        self._broadcast.stop()
        self.__threads.stop()
        self._connection.close()
        self.config.save()

    def restart(self):
        self.stop()
        log.warn('Restarting worker process')
        pt.restart_program()

    def process(self, request, properties):
        try:
            if not isinstance(request, pt.protocol.Request):
                raise TypeError('Can handle only requests. Something strange received: %s' % request)

            origin = properties.reply_to
            if isinstance(request, pt.request.DiscoveryRequest):
                self.send_discovery_response(target=origin, reply_on=request)

            if isinstance(request, pt.RestartRequest):
                self.restart()

            if isinstance(request, pt.ExecuteRequest):
                scenario = pt.scenarios.ExecuteScript(request.script, cwd=request.cwd)
                callback = lambda: self.send_execute_response(scenario, origin, request)
                try:
                    scenario.start(request.timeout, callback)
                except pt.scenarios.TimeoutError, e:
                    log.error(e)
                    self.send_timeout_response(scenario, origin, request)

            if isinstance(request, pt.TerminateRequest):
                pt.disable_auto_restart()
                self.stop()

        except Exception, e:
            log.error('Exception during processing:%s\nrequest=%s\nproperties=%s', e, request, properties)

    def send_execute_response(self, scenario, origin, request):
        response = pt.ExecuteResponse(result=scenario.status(), output=scenario.result())
        self._sender.send(response, target=origin, reply_on=request)

    def send_discovery_response(self, target=None, reply_on=None):
        response = pt.response.DiscoveryResponse()
        self._sender.send(response, target=target, reply_on=reply_on)

    def send_timeout_response(self, scenario, origin, request):
        log.warning('Timeout for scenario. Responding with timeout response')
        response = pt.response.ExecuteResponse(result=-1, output='Timeout: %s.' % scenario.result)
        self._sender.send(response, target=origin, reply_on=request)
