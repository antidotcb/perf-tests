__author__ = 'Danylo Bilyk'

import pt
from orchestrator import Orchestrator

if __name__ == '__main__':
    pt.enable_auto_restart(10)
    orchestrator = Orchestrator()
    orchestrator.start()
