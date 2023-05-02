#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 17:05:49 2021

@author: danielsavage
"""

from setuptools import setup
from setuptools import find_packages
setup(name='MILK',
      version='0.3',
      description='MAUD Interface Tool Kit',
      url='https://github.com/lanl/MILK.git',
      author='Daniel Savage',
      author_email='dansavage@lanl.gov',
      license='BSD 3',
      packages=find_packages(),
      scripts=["bin/config_maud.py", "bin/maudText.py", "bin/cinema.py", "bin/difftools-1dhistogram-contour.py",
               "bin/difftools-ge2fabIO.py", "bin/difftools-integrate-mg.py", "bin/difftools-maud-esg-loader.py"],
      install_requires=[],
      zip_safe=False)
