#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 20:22:15 2021

@author: danielsavage
"""

import os
import shutil

def hippo_texture():
    fn = os.path.join(os.path.dirname(__file__),'resources/data/HIPPO/U6')
    shutil.copytree(fn,os.path.join(os.getcwd(),'U6'))
        
def hippo_texture_multiphase():
    fn = os.path.join(os.path.dirname(__file__),'resources/data/HIPPO/steel')
    shutil.copytree(fn,os.path.join(os.getcwd(),'steel'))

def lcls_shocked_texture_and_multiphase():
    fn = os.path.join(os.path.dirname(__file__),'resources/data/LCLS/Ti')
    shutil.copytree(fn,os.path.join(os.getcwd(),'Ti'))
