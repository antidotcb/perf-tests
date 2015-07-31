__author__ = 'Danylo Bilyk'

import os
import platform
import subprocess

from .scenario import Scenario


class ExecuteScript(Scenario):
    SCRIPTS_DIR = 'scripts'
    WINDOWS_SYSTEM = 'Windows'
    LINUX_SCRIPT_EXTENSION = 'sh'
    WINDOWS_SCRIPT_EXTENSION = 'bat'

    def __init__(self, command, cwd=None, *args, **kwargs):
        self._cwd = cwd
        self._pid = 0
        self._args = ExecuteScript.__prepare_script_args(command)
        super(ExecuteScript, self).__init__(self._args[0], *args, **kwargs)

    def _exec_run(self, *args, **kwargs):
        self._status = None
        try:
            process = subprocess.Popen(self._args, cwd=self._cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
            result = process.communicate()
            self._status = process.returncode
            self._pid = process.pid
            return result
        except WindowsError, e:
            self._status = e.winerror
            result = (None, str(e))
        return result

    def _post_run(self, callback=None, *args, **kwargs):
        stdout, stderr = self._result
        if stderr:
            self._result = stderr
        else:
            self._result = stdout
        if callback:
            callback()

    @staticmethod
    def __prepare_script_args(command):
        args = command.split()
        ext = ExecuteScript.__get_platform_extension()
        filename = args[0] + os.extsep + ext
        args[0] = os.path.join(os.getcwd(), ExecuteScript.SCRIPTS_DIR, filename)
        return args

    @staticmethod
    def __get_platform_extension():
        ext = ExecuteScript.LINUX_SCRIPT_EXTENSION
        if ExecuteScript.WINDOWS_SYSTEM in platform.system():
            ext = ExecuteScript.WINDOWS_SCRIPT_EXTENSION
        return ext
