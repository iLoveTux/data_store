#!/usr/bin/env python

from setuptools import setup

setup(name='data_store',
      version='0.6.0',
      description='A MongoDB inspired data_store',
      author='iLoveTux',
      author_email='me@ilovetux.com',
      maintainer="ilovetux",
      url='https://ilovetux.com/products/data_store',
      packages=['data_store'],
      license="GPL v2",
      install_requires=["bottle == 0.12.8"]
     )
