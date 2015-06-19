from setuptools import setup, find_packages

setup(
    name="pt_common",
    version='0.0.1',
    author='Danylo Bilyk',
    author_email='danylo.bilyk@eglobal-forex.com',
    description='The common libraries shared between Client & Server',
    packages=find_packages(where='src/pt', exclude=['scenario_scripts']),
    install_requires=['pika'],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage']
    },
    package_data={
        'scenario_scripts': ['scenario_scripts/*']
    },
)
