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
        super(ExecuteScript, self).__init__(self._args[0], **kwargs)

    def _exec_run(self, *args, **kwargs):
        sp = subprocess
        p = sp.Popen(self._args, cwd=self._cwd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT)
        p.communicate()

        p.stdin.close()

        chunks = []

        while True:
            try:
                chunk = p.stdout.read(4096)
                if not chunk:
                    break
                chunks.append(chunk)
            except IOError, ex:
                if ex[0] != errno.EAGAIN:
                    raise
                sys.exc_clear()

        p.stdout.close()
        return ''.join(chunks)
