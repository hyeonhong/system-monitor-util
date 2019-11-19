#!/usr/bin/env bash

cd monitor_usage
pip3 install virtualenv
virtualenv env
source env/bin/activate
pip3 install -r requirements.txt
python3 monitor_usage.py
deactivate
rm -rf env
