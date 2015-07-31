__author__ = 'Danylo Bilyk'

import pt

from orchestrator import Orchestrator

if __name__ == '__main__':
    pt.AutoRestart.enable()
    orchestrator = Orchestrator()
    orchestrator.run()
