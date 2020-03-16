
#! /bin/bash

coverage run --omit=air_sdk/tests/*,*/__init__.py --source='./air_sdk' `which pytest` air_sdk
coverage report
coverage html
