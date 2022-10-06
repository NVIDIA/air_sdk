# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

""" Setup script """

import setuptools

with open('README.md', 'r') as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name='air-sdk',
    version='2.3.0',
    author='Mike Robertson',
    author_email='mrobertson@nvidia.com',
    description='Python SDK for interacting with NVIDIA Air',
    license='MIT',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/NVIDIA/air_sdk',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=['python-dateutil', 'requests']
)
