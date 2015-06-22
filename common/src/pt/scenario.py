__author__ = 'Danylo Bilyk'
import time


class Scenario:
    def __init__(self, name):
        self.name = name
        pass

    def run(self):
        print "Start scenario execution:", self.name
        time.sleep(1)
        print "End scenario execution:", self.name
        return 0
