#! /bin/bash
# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

python3 -m coverage run -m pytest
coverage report -m
coverage html
