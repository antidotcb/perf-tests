from setuptools import setup, find_packages

setup(
    name='pt_common',
    version='0.0.2',
    author='Danylo Bilyk',
    url='https://github.com/antidotcb/perf-tests',
    author_email='danylo.bilyk@eglobal-forex.com',
    description='The common libraries shared between Client & Server',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=['pika', 'pymongo'],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage']
    },
    package_data={
        'scenario_scripts': ['scenario_scripts/*']
    },
)
