import os

from setuptools import setup

setup(
    version=os.environ.get("PACKAGE_VERSION", "0.0.0-dev")
)
