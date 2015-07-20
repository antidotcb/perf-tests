__author__ = 'Danylo Bilyk'

from pt import log

import pt


class Worker(object):
    def __init__(self):
        self.info = pt.WorkerInfo.own()

        self._conn = pt.Connection(**pt.config.connection())

        exchanges = pt.config.exchanges()

        self._conn.create_exchange(exchanges['broadcast'], 'fanout')
        self._conn.create_exchange(exchanges['direct'], 'direct')

        self._broadcast = pt.protocol.Listener(self._conn, exchanges['broadcast'], self.process)
        self._direct = pt.protocol.Listener(self._conn, exchanges['direct'], self.process, routing_key=self.info.uuid)

        self._sender = pt.protocol.Sender(self._conn, exchanges['direct'])

        self.__threads = pt.ThreadCollection()
        self.__threads.append(self._broadcast.start)
        self.__threads.append(self._direct.start)

    def start(self):
        self.__threads.start()
        self.send_startup_notification()
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

            if isinstance(request, pt.request.DiscoveryRequest):
                self._sender.send(pt.response.DiscoveryResponse(), to=properties.reply_to,
                                  reply_on=properties.message_id)

            if isinstance(request, pt.RestartRequest):
                self.restart()

            if isinstance(request, pt.ExecuteRequest):
                scenario = pt.scenarios.ExecuteScript(request.script, cwd=request.cwd)
                scenario.start(request.timeout)
                self._sender.send(pt.ExecuteResponse(result=scenario.status(), output=scenario.result()),
                                  to=properties.reply_to)

            if isinstance(request, pt.TerminateRequest):
                pt.disable_auto_restart()
                self.stop()

        except Exception, e:
            log.error('Exception during processing:%s\nrequest=%s\npropeties=%s', e, request, properties)

    def send_startup_notification(self):
        self._sender.send(pt.response.DiscoveryResponse())
