#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 13:43:23 2021

@author: danielsavage
"""

from MILK.data import (generateGroup, prepareData, examples, lcls)
from MILK.interface import (parameterEditor, addPhase)
from MILK.interface.model import (texture, sizeStrain)
from MILK.MAUDText import maud
from MILK.MAUDText.callMaudText import resource_file_path
from MILK.environment.initilize import load_json
import os
import sys


# Add resources to the search path
curpath = os.path.dirname(os.path.realpath(__file__))
resourceList = ['MILK/interface/model/resources',
                'MILK/MAUDText/resources', 'resources', 'MILK/environment/resources']
for resource in resourceList:
    sys.path.append(os.path.join(curpath[0:-5], resource))

myconst = 1
