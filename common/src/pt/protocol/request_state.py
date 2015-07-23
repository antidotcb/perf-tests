__author__ = 'Danylo Bilyk'

import threading

from pt.protocol import ResponseDetails

from pt.utils import synchronous


class RequestState(object):
    def __init__(self, timeout, request, targets='', on_timeout=None, on_collect=None, on_responded=None):
        self._object_lock = threading.RLock()
        self.request = request
        self.targets = targets
        self.__collect_cb = on_collect
        self.__responded_cb = on_responded
        # just stupid simple sleep in case no on_timeout callback specified
        self.__timeout_callback = on_timeout if on_timeout else lambda: None
        self.__timeout_timer = threading.Timer(timeout, self.__timeout_callback)
        self.__responses = {}
        self.__responded = False

    @synchronous('_object_lock')
    def _set_responded(self, responded=True):
        self.__responded = responded

    @synchronous('_object_lock')
    def is_responded(self):
        return self.__responded

    @synchronous('_object_lock')
    def get_response_details(self):
        return self.__responses.itervalues()

    def not_responded(self):
        return [target for target in self.targets if target not in self.__responses.keys()]

    @synchronous('_object_lock')
    def collect_response(self, response, properties):
        if self.request.id != properties.correlation_id:
            raise AttributeError('Response do not belong to this request')
        if self.__collect_cb:
            processed = self.__collect_cb(response, properties)
            if processed is False:
                return  # unacceptable response if function return False
        if response.uuid in self.__responses.keys():
            raise KeyError('Duplicate responses from uuid %s' % response.uuid)
        self.__responses[response.uuid] = ResponseDetails(response, properties)
        # cancel timeout callback if all request recipients responded
        if self.targets and set(self.targets) == set(self.__responses.keys()):
            self.__timeout_timer.cancel()
            self._set_responded()

    def wait_for_responses(self):
        self.__timeout_timer.start()
        self.__timeout_timer.join()
        if self.__responded_cb:
            self.__responded_cb(self)
