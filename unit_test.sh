#! /bin/bash
# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

python3 -m coverage run --omit=.tests/*,*/__init__.py --source='./air_sdk' -m pytest -s tests/*
coverage report
coverage html
