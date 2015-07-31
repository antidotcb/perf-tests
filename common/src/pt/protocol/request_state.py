__author__ = 'Danylo Bilyk'

import threading
import time

from pt.protocol import ResponseDetails
from pt.utils import synchronous, log


class RequestState(object):
    def __init__(self, request, targets=None, on_timeout=None, on_collect=None):
        self._object_lock = threading.RLock()
        self.request = request
        self.targets = targets
        self.__targets_id = [target.uuid for target in self.targets] if self.targets else None
        self.__collect_cb = on_collect
        self.__responses = {}
        self.__responded = False
        self.__timeout_timer = None
        self.__timeout_callback = on_timeout if on_timeout else lambda x: None
        # just stupid simple sleep in case no on_timeout callback specified
        if on_timeout:
            self.__timeout_timer = threading.Timer(request.request_timeout(), self.__timeout_callback, (self,))

    @synchronous('_object_lock')
    def __set_responded(self, responded):
        self.__responded = responded

    @synchronous('_object_lock')
    def is_responded(self):
        return self.__responded

    @synchronous('_object_lock')
    def get_response_details(self):
        return self.__responses.itervalues()

    @synchronous('_object_lock')
    def not_responded(self):
        return [target for target in self.targets if target not in self.responded()]

    @synchronous('_object_lock')
    def responded(self):
        return self.__responses.keys()

    @synchronous('_object_lock')
    def collect_response(self, response, properties):
        if self.request.id != properties.correlation_id:
            raise AttributeError('Response do not belong to this request')
        if self.__collect_cb:
            try:
                if self.request.response_type() != response.__class__:
                    raise TypeError('Unacceptable response for this request.')
                self.__collect_cb(response, properties)
            except Exception, e:
                log.error('Response is not processed. Internal exception: %s', e)
                return
        if response.uuid in self.__responses.keys():
            raise KeyError('Duplicate responses from uuid %s' % response.uuid)
        self.__responses[response.uuid] = ResponseDetails(response, properties)
        if self.__targets_id and set(self.__targets_id) == set(self.responded()):
            self.__set_responded(True)
            self.__cancel_timer()

    def wait_for_responses(self):
        if self.__timeout_timer:
            self.__wait_for_timer()
        else:
            time.sleep(self.request.request_timeout())

    def __cancel_timer(self):
        if self.__timeout_timer:
            self.__timeout_timer.cancel()
            self.__timeout_callback(self)

    def __wait_for_timer(self):
        self.__timeout_timer.start()
        self.__timeout_timer.join()
