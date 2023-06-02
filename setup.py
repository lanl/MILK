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
      entry_points={
          'console_scripts': [
              'milk-config = bin.milk_config:main',
              'milk-maudText = bin.milk_maudText:main',
              'milk-cinema = bin.milk_cinema:main',
              'milk-1dhistogram-contour = bin.milk_1dhistogram_contour:main',
              'milk-ge2fabIO = bin.milk_ge2fabIO:main',
              'milk-integrate = bin.milk_integrate:main',
              'milk-esg-loader = bin.milk_esg_loader:main',
              'milk-poni-export = bin.milk_poni_export:entry_point',
              'milk-examples = bin.milk_examples:main'
          ],
      },
      install_requires=[],
      zip_safe=False)
