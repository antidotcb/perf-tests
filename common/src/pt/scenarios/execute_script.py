__author__ = 'Danylo Bilyk'

import os
import platform
import subprocess

from .scenario import Scenario


def _prepare_script_args(command):
    path = os.getcwd() + os.sep + 'scripts' + os.sep
    ext = 'bat' if 'Windows' in platform.system() else 'sh'
    script = path + command + os.extsep + ext
    return script.split()


class ExecuteScript(Scenario):
    def __init__(self, command, cwd=None, *args, **kwargs):
        self._cwd = cwd
        self._pid = 0
        self._args = _prepare_script_args(command)
        super(ExecuteScript, self).__init__(self._args[0], *args, **kwargs)

    def _exec_run(self, *args, **kwargs):
        self._status = -1

        sp = subprocess
        process = None
        result = None
        try:
            process = sp.Popen(self._args, cwd=self._cwd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT)
        except WindowsError, e:
            self._status = -1
            result = (None, str(e))
        if process:
            result = process.communicate()
            self._status = process.returncode
            self._pid = process.pid
        return result

    def _post_run(self, callback=None, *args, **kwargs):
        stdout, stderr = self._result
        if stderr:
            self._result = stderr
        else:
            self._result = stdout
        if callback:
            callback()
