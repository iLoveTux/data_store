#!/usr/bin/env python

from setuptools import setup

setup(name='data.store',
      version='0.6.7.1',
      #description='a simple mongo-esque data_store.',
      author='iLoveTux',
      author_email='me@ilovetux.com',
      maintainer="ilovetux",
      url='https://github.com/iLoveTux/data_store',
      packages=['data', 'data.store'],
      license="GPL v2",
      install_requires=["bottle == 0.12.8"]
     )
