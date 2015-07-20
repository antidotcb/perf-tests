__author__ = 'Danylo Bilyk'

import pt
from pt import log


class Worker(object):
    def __init__(self):
        self.info = pt.WorkerInfo.own()

        self._conn = pt.Connection(**pt.config.connection())

        exchanges = pt.config.exchanges()

        self._conn.create_exchange(exchanges['broadcast'], 'fanout')
        self._conn.create_exchange(exchanges['direct'], 'direct')

        self._broadcast = pt.protocol.Listener(self._conn, exchanges['broadcast'], self.process)
        self._direct = pt.protocol.Listener(self._conn, exchanges['direct'], self.process, routing_key=self.info.name)

        self._sender = pt.protocol.Sender(self._conn, exchanges['direct'], default_send_to='orc')

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
                self._sender.send(pt.ExecuteResult(result=scenario.status(), output=scenario.result()),
                                  to=properties.reply_to)

        except Exception, e:
            log.error('Exception during execution of script (%s): %s', request.script, e)

    def send_startup_notification(self):
        self._sender.send(pt.response.DiscoveryResponse())
