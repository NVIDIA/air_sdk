#! /bin/bash
# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

coverage run --omit=.tests/*,*/__init__.py --source='./air_sdk' `which pytest` tests/*
coverage report
coverage html
