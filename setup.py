#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 17:05:49 2021

@author: danielsavage
"""

from setuptools import setup
from setuptools import find_packages
setup(name='MILK',
      version='0.1',
      description='MAUD Interface Tool Kit',
      url='https://github.com/lanl/MILK.git',
      author='Daniel Savage',
      author_email='dansavage@lanl.gov',
      license='BSD 3',
      packages=find_packages(),
      install_requires=[],
      zip_safe=False)
