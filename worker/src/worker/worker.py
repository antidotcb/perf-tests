__author__ = 'Danylo Bilyk'

from pt import log

from pt.scenarios import TimeoutError
import pt


class Worker(object):
    def __init__(self):
        self.info = pt.WorkerInfo.own()

        self._conn = pt.Connection(**pt.config.connection())

        exchanges = pt.config.exchanges()

        self._conn.create_exchange(exchanges['broadcast'], 'fanout')
        self._conn.create_exchange(exchanges['direct'], 'direct', durable=True)

        self._broadcast = pt.protocol.Listener(self._conn, exchanges['broadcast'], self.process)
        self._direct = pt.protocol.Listener(self._conn, exchanges['direct'], self.process, routing_key=self.info.uuid)

        self._sender = pt.protocol.Sender(self._conn, exchanges['direct'])

        self.__threads = pt.ThreadCollection()
        self.__threads.add(self._broadcast.start)
        self.__threads.add(self._direct.start)

    def start(self):
        self.__threads.start()
        self.send_discovery_response()
        self.__threads.join()

    def stop(self):
        self._direct.stop()
        self._broadcast.stop()
        self.__threads.stop()
        self._conn.close()

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
                except TimeoutError:
                    self.send_timeout_response(scenario, origin, request)

            if isinstance(request, pt.TerminateRequest):
                pt.disable_auto_restart()
                self.stop()

        except Exception, e:
            log.error('Exception during processing:%s\nrequest=%s\npropeties=%s', e, request, properties)

    def send_execute_response(self, scenario, origin, request):
        response = pt.ExecuteResponse(result=scenario.status(), output=scenario.result())
        self._sender.send(response, target=origin, reply_on=request)

    def send_discovery_response(self, target=None, reply_on=None):
        self._sender.send(pt.response.DiscoveryResponse(), target=target, reply_on=reply_on)

    def send_timeout_response(self, scenario, origin, request):
        log.warning('Timeout for scenario. Responding with timeout response')
        response = pt.response.ExecuteResponse(result=-1, output='Timeout: %s.' % scenario.result)
        self._sender.send(response, target=origin, reply_on=request)
