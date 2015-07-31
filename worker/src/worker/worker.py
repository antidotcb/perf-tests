__author__ = 'Danylo Bilyk'

import os.path
import shutil
import time

import pt
from pt.utils import config, log
from .collector import LogCollector


class Worker(object):
    def __init__(self):
        self._connection = pt.Connection(**config.connection())

        exchanges = config.exchanges()

        self._connection.create_exchange(exchanges['broadcast'], 'fanout')
        self._connection.create_exchange(exchanges['direct'], 'direct', durable=True)

        self._broadcast = pt.protocol.Listener(self._connection, exchanges['broadcast'], self.process)
        self._direct = pt.protocol.Listener(self._connection, exchanges['direct'], self.process,
                                            routing_key=config.uuid())

        self._sender = pt.protocol.Sender(self._connection, exchanges['direct'])

        self.__threads = pt.ThreadCollection()
        self.__threads.add(self._broadcast.start)
        self.__threads.add(self._direct.start)

    def run(self):
        self.__threads.start()
        self.__threads.join()

    def stop(self):
        self._direct.stop()
        self._broadcast.stop()
        self.__threads.stop()
        config.save()

    def restart(self):
        self.stop()
        log.warn('Restarting worker process')
        pt.AutoRestart.perform_restart()

    def process(self, request, properties):
        try:
            if not isinstance(request, pt.protocol.Request):
                raise TypeError('Can handle only requests. Something strange received: %s' % request)

            origin = pt.Worker(uuid=properties.reply_to)
            if isinstance(request, pt.request.DiscoveryRequest):
                self.send_discovery_response(origin, reply_on=request)
            elif isinstance(request, pt.RestartRequest):
                self.restart()
            elif isinstance(request, pt.ExecuteRequest):
                scenario = pt.scenarios.ExecuteScript(request.script, cwd=request.cwd)
                callback = lambda: self.send_execute_response(scenario, origin, request)
                try:
                    scenario.start(request.timeout, callback)
                except pt.scenarios.TimeoutError, e:
                    log.error(e)
                    self.send_timeout_response(scenario, origin, request)
            elif isinstance(request, pt.TerminateRequest):
                pt.AutoRestart.disable()
                self.stop()
            elif isinstance(request, pt.BackupRequest):
                try:
                    collector = LogCollector(request.test_start_time)
                    backup_root = config.get_option('backup_store_directory', 'BACKUP')

                    directories = config.get_option('collect_directories', 'BACKUP')
                    extension = config.get_option('collect_extension', 'BACKUP')
                    collect_root = config.get_option('collect_root', 'BACKUP')

                    timestamp_dir = os.path.join(backup_root, '%s' % time.ctime(request.test_start_time).replace(':','').replace(' ','_'))
                    for directory in directories.split(';'):
                        collect_dir = os.path.join(collect_root, directory)
                        backup_dir = os.path.join(timestamp_dir, directory)
                        collected_files = collector.collect(collect_dir)
                        if not os.path.exists(backup_dir):
                            self._mkdir_recursive(backup_dir)
                        for collected_file in collected_files:
                            relative_name = collected_file[len(collect_dir):] if collected_file.startswith(collect_dir) else collected_file
                            target_file = backup_dir + relative_name
                            target_file_dir = os.path.dirname(target_file)
                            if not os.path.exists(target_file_dir):
                                self._mkdir_recursive(target_file_dir)
                            print collected_file
                            print target_file
                            shutil.copy(collected_file, target_file)
                except Exception, e:
                    log.error(e)
            else:
                log.warning('Request %s is not processed. Please update worker.', request)

        except Exception, e:
            log.error('Exception during processing:%s\nrequest=%s\nproperties=%s', e, request, properties)

    def _mkdir_recursive(self, path):
        sub_path = os.path.dirname(path)
        if not os.path.exists(sub_path):
            self._mkdir_recursive(sub_path)
        if not os.path.exists(path):
            os.mkdir(path)

    def send_execute_response(self, scenario, origin, request):
        response = pt.ExecuteResponse(result=scenario.status(), output=scenario.result())
        self._sender.send(response, targets=origin, reply_on=request)

    def send_discovery_response(self, origin, reply_on=None):
        response = pt.response.DiscoveryResponse()
        self._sender.send(response, targets=origin, reply_on=reply_on)

    def send_timeout_response(self, scenario, origin, request):
        log.warning('Timeout for scenario. Responding with timeout response')
        response = pt.response.ExecuteResponse(result=-1, output='Timeout: %s.' % scenario.result)
        self._sender.send(response, targets=origin, reply_on=request)
