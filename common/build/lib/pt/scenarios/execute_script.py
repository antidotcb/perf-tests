__author__ = 'Danylo Bilyk'

import errno
import subprocess
import sys

# import fcntl
from .scenario import Scenario


class ExecuteScript(Scenario):
    def __init__(self, command, cwd=None, **kwargs):
        self._args = command.split()
        self._cwd = cwd
        self._pid = 0
        super(ExecuteScript, self).__init__(self._args[0], **kwargs)

    def _exec_run(self, *args, **kwargs):
        sp = subprocess
        p = sp.Popen(self._args, cwd=self._cwd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT)
        output = p.communicate()
        self._status = p.returncode
        self._pid = p.pid
        return output
