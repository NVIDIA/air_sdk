
#! /bin/bash

coverage run --omit=.tests/*,*/__init__.py --source='./air_sdk' `which pytest` tests/*
coverage report
coverage html
