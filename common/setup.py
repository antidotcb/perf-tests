from setuptools import setup, find_packages

setup(
    name='pt_common',
    version='0.0.3',
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
    }
)

'''
Component coordinate performance test execution

Start test
    Reset MT4 servers
    Sends request to Rack-Space controller
    Wait till all MT4 servers are up
    Wait till Rack-Space has created all terminal servers
    Notifies about successful test start

Stop test
    Send request to Rack-Space to kill all MT4 terminal servers
    Send message to MT4 servers to stop
    Publish all logs and databases
    Collects all logs and databases
    Generates report
'''