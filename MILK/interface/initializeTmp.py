#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 10:30:46 2021

@author: danielsavage
"""

import environment
import os
import shutil              


def main():
    shutil.copyfile(environment.par_input, environement.par_tmp)
    
if __name__ == '__main__':
    main([])