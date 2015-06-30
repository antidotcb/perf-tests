__author__ = 'Danylo Bilyk'

import subprocess
import errno
import sys
import os

import fcntl

from .scenario import Scenario


class ExecuteScript(Scenario):
    def __init__(self, script_name, **kwargs):
        self._args = script_name.split()
        super(ExecuteScript, self).__init__(self._args[0], **kwargs)

    def _exec_run(self, *args, **kwargs):
        p = subprocess.Popen(self._args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        fcntl.fcntl(p.stdin, fcntl.F_SETFL, os.O_NONBLOCK)  # make the file nonblocking
        fcntl.fcntl(p.stdout, fcntl.F_SETFL, os.O_NONBLOCK)  # make the file nonblocking

        bytes_total = len(data)
        bytes_written = 0
        while bytes_written < bytes_total:
            try:
                # p.stdin.write() doesn't return anything, so use os.write.
                bytes_written += os.write(p.stdin.fileno(), data[bytes_written:])
            except IOError, ex:
                if ex[0] != errno.EAGAIN:
                    raise
                sys.exc_clear()
            socket.wait_write(p.stdin.fileno())

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
            socket.wait_read(p.stdout.fileno())

        p.stdout.close()
        return ''.join(chunks)
