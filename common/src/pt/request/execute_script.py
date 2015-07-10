__author__ = 'Danylo Bilyk'

from pt.protocol import Request
from pt.protocol import ProtocolMessage
from pt.scenarios import ExecuteScript
from pt.utils import log
from pt.response import ScriptResult


class ExecuteRequest(Request):
    __metaclass__ = ProtocolMessage

    _DEFAULTS = {
        'script': None,
        'cwd': 'c:\\work\\perf-tests',
    }

    def __init__(self, *args, **kwargs):
        super(ExecuteRequest, self).__init__(*args, **kwargs)
        self._scenario = ExecuteScript(self.script, cwd=self.cwd)

    def perform(self):
        if self._is_target():
            try:
                output = self._scenario.run()
                return ScriptResult(result=self._scenario.status(), output=output)
            except Exception, e:
                log.error('Exception during execution of script (%s): %s', self.script, e.message)
