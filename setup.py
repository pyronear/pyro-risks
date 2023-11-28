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

PACKAGE_NAME = "pyro_risks"
VERSION = "0.0.1"


with open("README.md") as f:
    readme = f.read()

requirements = [
    "boto3==1.28.45",
    "botocore==1.31.45",
    "Rtree>=0.9.4",
    "Shapely>=1.7.1",
    "netCDF4>=1.5.4",
    "requests>=2.24.0",
    "xarray>=0.16.1",
    "scipy>=1.5.4",
    "scikit-learn>=0.23.2",
    "imbalanced-learn>=0.7.0",
    "xgboost==1.2.1",
    "xlrd==1.2.0",
    "numpy>=1.18.5",
    "cdsapi==0.4.0",
    "python-dotenv>=0.15.0",
    "plot-metric==0.0.6",
    "dvc>=2.0.5",
    "dvc[gdrive]>=2.0.5",
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
    entry_points={"console_scripts": ["pyrorisks = pyro_risks.main:main"]},
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
