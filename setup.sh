#!/bin/bash
pip install virtualenv
virtualenv .env
source .env/bin/activate
pip install -e common
