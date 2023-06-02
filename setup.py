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
      scripts=["bin/milk-config.py", "bin/milk-maudText.py", "bin/milk-cinema.py", "bin/milk-1dhistogram-contour.py",
               "bin/milk-ge2fabIO.py", "bin/milk-integrate.py", "bin/milk-esg-loader.py", "bin/milk-poni-export.py",
               "bin/milk-examples.py"],
      entry_points={
          'console_scripts': [
              'config2 = MILK.bin.milk_config:main',
          ],
      },
      install_requires=[],
      zip_safe=False)
