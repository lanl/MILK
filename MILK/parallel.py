#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 15 10:41:10 2022.

@author: danielsavage
"""
# Setup integration
from pathos.pools import ProcessPool as pPool
from pathos.helpers import cpu_count
from functools import partial
from tqdm import tqdm

def serial_map(func, poolsize: int, disable_tqdm: bool, loop_arg:list, *args):
    """Do parallel computing with function and tqdm progress bar."""
    # map_size = len(loop_arg)
    # if map_size==1:
    #     func2 = partial(func,*args)
    #     return list(func2(loop_arg[0]))
    # else:
    mapper = map
    loop_arg = list(loop_arg)
    return list(tqdm(mapper(partial(func,*args),
                            loop_arg), total=len(loop_arg),disable=disable_tqdm))


def parallel_map(func, poolsize: int, disable_tqdm: bool, loop_arg:list, *args):
    """Do parallel computing with function and tqdm progress bar."""
    if poolsize == 1:
        return serial_map(func, poolsize, disable_tqdm, loop_arg, *args)

    with pPool(poolsize) as pool:
        mapper = pool.imap
        loop_arg = list(loop_arg)
        return list(tqdm(mapper(partial(func,*args),
                                loop_arg), total=len(loop_arg),disable=disable_tqdm))

def get_ncpus():
    return cpu_count()