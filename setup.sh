#!/bin/bash
pip install virtualenv
virtualenv .env
source .env/bin/activate
pip install -e common
pip show pt-common

git config core.autocrlf true
git config user.email "daniil.bilyk@eglobal-forex.com"
git config user.name "Danylo Bilyk"
git update-index --no-assume-unchanged config.ini
