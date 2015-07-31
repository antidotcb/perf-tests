__author__ = 'Danylo Bilyk'

from os import walk
import os.path
import os.path
import time


class FileState(object):
    def __init__(self, name, size, created, modified):
        self.name = name
        self.size = size
        self.created = created
        self.modified = modified

    def __str__(self):
        mask = "name: %s, size: %d, created: %s, modified: %s"
        return mask % (self.name, self.size, time.ctime(self.created), time.ctime(self.modified))


class LogCollector(object):
    def __init__(self, start_datetime):
        self.start_datetime = start_datetime

    def collect_file_states(self, directory, recursive=False):
        result = {}
        for (root, sub_dirs, files) in walk(directory):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                result[file_path] = self.get_file_state(file_path)

            if recursive:
                for dir_name in sub_dirs:
                    sub_dir = os.path.join(root, dir_name)
                    sub_result = self.collect_file_states(sub_dir)
                    result.update(sub_result)
        return result

    def detect_modification(self, directory, timestamp):
        states = self.collect_file_states(directory)
        result = []
        for path, state in states.iteritems():
            if state.modified > timestamp:
                print state
                result.append(path)
        return result

    @staticmethod
    def get_file_state(filename):
        if not os.path.isfile(filename):
            raise AttributeError('File %s does not not exist', filename)

        size = os.path.getsize(filename)
        creation = os.path.getctime(filename)
        modification = os.path.getmtime(filename)

        return FileState(filename, size, creation, modification)

    def collect(self, directory):
        timestamp = self.start_datetime
        return self.detect_modification(directory, timestamp)
