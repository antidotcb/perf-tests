__author__ = 'Danylo Bilyk'

import os
import platform
import subprocess

from .scenario import Scenario


class ExecuteScript(Scenario):
    def __init__(self, command, cwd=None, **kwargs):
        path = os.getcwd() + os.sep + 'scripts' + os.sep
        ext = 'bat' if 'Windows' in platform.system() else 'sh'
        script = path + command + os.extsep + ext
        self._args = script.split()
        self._cwd = cwd
        self._pid = 0
        super(ExecuteScript, self).__init__(self._args[0], **kwargs)

    def _exec_run(self, *args, **kwargs):
        sp = subprocess
        p = sp.Popen(self._args, cwd=self._cwd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT)
        result = p.communicate()
        self._status = p.returncode
        self._pid = p.pid
        return result

    def _post_run(self, *args, **kwargs):
        stdout, stderr = self._result
        if stderr:
            self._result = stderr
        for line in stdout.split(os.linesep):
            if 'Already up-to-date.' in line:
                self._result = line.strip()
