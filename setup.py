# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

#!usr/bin/python

"""
Package installation setup
"""

import os
import subprocess
from setuptools import setup, find_packages

PACKAGE_NAME = "pyrorisks"
VERSION = "0.0.1"


with open("README.md") as f:
    readme = f.read()

requirements = [
    "boto3==1.28.45",
    "botocore==1.31.45",
    "click==8.1.7",
    "geopandas==0.13.2",
    "pandas==2.1.0",
    "python-dotenv==1.0.0",
    "rasterio==1.3.9",
    "requests==2.31.0",
    "numpy==1.26.4",
    "sphinx_rtd_theme",
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author="Pyronear Contributors",
    description="Pre-processing pipelines and models for wildfire forecasting and monitoring",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/pyronear/pyro-risks",
    download_url="https://github.com/pyronear/pyro-risks/tags",
    license="GPLv3",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["data science", "time series", "machine learning"],
    packages=find_packages(exclude=("test",)),
    zip_safe=True,
    python_requires=">=3.6.0",
    include_package_data=True,
    install_requires=requirements,
    package_data={"": ["LICENSE"]},
)
