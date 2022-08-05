#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 10:41:30 2021

@author: danielsavage
"""

import json


def load_json(fname: str):
    with open(fname, 'r') as f:
        data = json.load(f)
    return data
