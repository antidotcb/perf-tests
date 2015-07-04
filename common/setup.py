from setuptools import setup, find_packages

setup(
    name='pt_common',
    version='0.0.2',
    author='Danylo Bilyk',
    url='https://github.com/antidotcb/perf-tests',
    author_email='danylo.bilyk@eglobal-forex.com',
    description='The common libraries shared between Workers & Orchestrator',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=['pika', 'pymongo', 'pyreadline'],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage']
    },
    package_data={
        'scenario_scripts': ['scenario_scripts/*']
    },
)
'''
Write main component, that will coordinate performance test execution
start test
Send message to rabbitmq to reset MT4 servers
Sends request to Rackspace controller
Wait till all MT4 servers are up (expectations via config)
Wait till rackspace has created all terminal servers
Notifies about successful test start
stop test
Send request to rackspace to kill all MT4 terminal servers
Send message to MT4 servers to stop and publish all logs and databases
Collects all logs and databases
Generates report
'''