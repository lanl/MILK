#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 15 10:41:10 2022.

@author: danielsavage
"""
import os
from pathlib import Path
from os.path import join, isdir, islink
import re
import json
from typing import List
import sys
import errno
import pandas as pd
import numpy as np


def unique_keys(list_of_dict: List[dict]):
    """
    Find unique keys in list of dictionaries.

    Parameters
    ----------
    list_of_dict : List[dict]
        List of dictionaries.

    Returns
    -------
    unique_keys : List[str]
        All unique keys in the .

    """
    # Get unique keys
    unique_keys = list(set(val for dic in list_of_dict for val in dic.keys()))
    return unique_keys


def read_maud_ini(fname: str):
    """
    Read MAUD ini from HIPPO.

    Parameters
    ----------
    fname : str
        File to read from.

    Returns
    -------
    dic : dict
        Dictionary of key value pars from MAUD ini.

    """
    with open(fname, 'r') as file:
        lines = file.readlines()
        dic = {}
        for line in lines:
            key, val = line.split(':')
            val = val.strip().split(',')
            if key not in dic.keys():
                dic[key] = []
            for v in val:
                dic[key].append(v)

        return dic


def read_file_linestr(in_file: str):
    """
    Read file as list of strings.

    Parameters
    ----------
    in_file : str
        File to read from.

    Returns
    -------
    lines : List[str]
        Each line in lines is a string.

    """
    with open(in_file) as f:
        lines = f.readlines()
        return lines


def write_file_linestr(lines: List[str], out_file: str):
    """
    Write file from list of strings.

    Parameters
    ----------
    lines : List[str]
        Each line in lines is a string.
    ofile : str
        Output file.

    Returns
    -------
    None.

    """
    with open(out_file, 'w') as f:
        f.writelines("%s\n" % line.strip('\n') for line in lines)


def test_contains(str1: str, str2: str, exact=True):
    """
    Find if str1 is a substrain or the same as str2.

    Parameters
    ----------
    str1 : str
        First string.
    str2 : str
        String test str1 for.
    exact : TYPE, optional
        Type of comparison. The default is True.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    if exact:
        return str1 == str2
    else:
        return str1 in str2


def search(keyword: str, directory=os.getcwd(), exact=True):
    """
    Look for a matching keyword in file name from a particular directory.

    Parameters
    ----------
    keyword : str
        A string of keyword or full file name to search for.
    directory : TYPE, optional
        The directory to start the search from. The default is MILK_dir().
    exact : TYPE, optional
        Match part (False) or all of the filename (True). The default is True.

    Returns
    -------
    file_list : TYPE
        DESCRIPTION.
    directory_list : TYPE
        DESCRIPTION.

    """
    file_list = []
    directory_list = []

    for root, dirs, files in sortedWalk(directory, topdown=True):
        for file in files:
            if test_contains(keyword, file, exact):
                directory_list.append(root)
                file_list.append(file)

    return file_list, directory_list


def sortedWalk(top, topdown=True, onerror=None):
    """
    Walk directory and return sorted directory lists.

    Parameters
    ----------
    top : Directory[str]
        Top of directory to walk.
    topdown : Bool, optional
        DESCRIPTION. The default is True.
    onerror : TYPE, optional
        DESCRIPTION. The default is None.

    Yields
    ------
    TYPE
        DESCRIPTION.

    """
    names = os.listdir(top)
    names.sort()
    dirs, nondirs = [], []

    for name in sorted(names, key=natural_keys):
        if isdir(os.path.join(top, name)):
            dirs.append(name)
        else:
            nondirs.append(name)

    if topdown:
        yield top, dirs, nondirs
    for name in dirs:
        path = join(top, name)
        if not os.path.islink(path):
            for x in sortedWalk(path, topdown, onerror):
                yield x
    if not topdown:
        yield top, dirs, nondirs


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):

    return [atoi(c) for c in re.split('(\d+)', text)]


def DL_to_LD(DL: dict):
    """
    Convert dictionary of list (DL) to list of dictionaries(LD).

    Note: MILK assumes if list length==1 that all values in the list have the same value

    Parameters
    ----------
    DL : dict
        dictionary of list.

    Returns
    -------
    LD : dict
        list of dictionaries(DL).

    """
    from numpy import nan

    length = max([len(v) for v in DL.values()])
    for k, v in DL.items():
        length_var = len(v)
        if length_var == 1:
            DL[k] = DL[k]*length
        elif length_var > 1 and length_var < length:
            DL[k].append([nan]*(length-length_var))
        elif length_var == 0:
            DL[k] = [nan]*length
    return [dict(zip(DL, i)) for i in zip(*DL.values())]


def LD_to_DL(LD: dict):
    """
    Convert list of dictionaries (LD) dictionary of list (DL).

    Note: MILK replaces an empty list with np.nan

    Parameters
    ----------
    LD : dict
        list of dictionaries.

    Returns
    -------
    DL : dict
        dictionary of list (DL).

    """
    return {k: [dic[k] for dic in LD] for k in LD[0]}


def D_to_DL(D: dict):
    """
    Make dictionary dictionary of list (DL).

    Parameters
    ----------
    D : dict
        Dictionary of various types.

    Returns
    -------
    DL : dict
        Dictionary of lists.

    """
    for k, v in D.items():
        if type(v) is not list:
            D[k] = [v]
    return D


def fill_DL(DL: dict):
    """
    Fill dictionary of lists according to the MILK convention.

    MILK convention is:
        1) empty lists becomes nans
        2) list of len==1 has the same value for all
        3) list of len>1 but less than max list len in dictionary are padded by nan

    Parameters
    ----------
    DL : dict
        dictionary of lists.

    Returns
    -------
    DL : dict
        dictionary of list (DL).

    """
    return LD_to_DL(DL_to_LD(DL))


def write_DL_to_csv(csv_name: str, DL: dict, over_write: bool = False):
    """
    Write dictionary of list to csv.

    Parameters
    ----------
    csv_name : str
        csv file name.
    DL : dict
        dictionary of lists.

    Returns
    -------
    None.

    """
    if over_write:
        from pandas import DataFrame
        # fill the DL, create data frame and write
        DL = fill_DL(DL)
        df = DataFrame(DL)
        df.to_csv(csv_name, index=False, header=True)
    else:
        print("Warning: database did not write because it already exists"
              " and overwrite is set to False")


def read_csv_to_DL(csv_name: str):
    """
    Read dictionary of list from csv.

    Parameters
    ----------
    csv_name : str
        csv file name.

    Returns
    -------
    DL : dict
        dictionary of lists.

    """
    from pandas import read_csv
    DL = read_csv(csv_name).to_dict(orient='list')

    # cleanup the stored lists
    for k, vs in DL.items():
        for i, v in enumerate(vs):
            if type(v) is str and '[' == v[0] and ']' == v[-1]:
                DL[k][i] = eval(v)
    return DL


def external_call(cmd, debug=False, use_system=False, write_Poutput=True, cwd: str = ""):
    """
    Call an external program with a list of commands.

    Parameters
    ----------
    cmd : List[str]
        Commands cat to call on the command.
    debug : BOOL, optional
        DESCRIPTION. The default is False.
    use_system : BOOL, optional
        Runing using os.system. The default is False.
    write_output : BOOL, optional
        If true and use_system false will write log and err files from Popen.
    cwd : str, optional
        Gives a working directory to write log and err files.

    Returns
    -------
    None.

    """
    assert type(cmd) is list, '_external_call takes a list of strings'
    from subprocess import Popen, PIPE
    from os import system
    if debug:
        print(" ".join(cmd))
    if use_system and debug:
        system(" ".join(cmd))
    elif use_system:
        system(" ".join(cmd) + [">", "/dev/null", "2>&1"])
    else:
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        if write_Poutput:
            log, err = p.communicate()
            write_file_linestr(lines=log.splitlines(),
                               out_file=os.path.join(cwd, 'output.log'))
            write_file_linestr(lines=err.splitlines(),
                               out_file=os.path.join(cwd, 'output.err'))


def get_maud_path(maud_path=os.getenv('MAUD_PATH')):
    """
    Read the MILK preferences file and raise error if path doesn't exist else return Maud Path.

    Parameters
    ----------
    maud_path : TYPE, optional
        DESCRIPTION. The default is os.getenv('MAUD_PATH').

    Raises
    ------
    error
        DESCRIPTION.
    FileNotFoundError
        DESCRIPTION.

    Returns
    -------
    maud_path : TYPE
        Path to Maud application.

    """
    if not os.path.exists(maud_path):
        message = "Set the MAUD path using config_maud.py in MILK/bin or specify in milk.json"
        raise FileNotFoundError(errno.ENOENT,
                                " ".join([os.strerror(errno.ENOENT), maud_path]),
                                message)
        return maud_path


# TODO update with java specific bits
def get_maud_exc():
    """
    Construct the full path to maud_exc bash/bat file that calls MAUD in text mode.

    Raises
    ------
    Exception
        If operating system is not yet supported.
    FileNotFoundError
        If path to bash/bat file does not exists.

    Returns
    -------
    maud_exc : TYPE
        Path to maud_exc bash/bat file.

    """
    # Construct the executable path
    file_path = os.path.basename(__file__)
    # for a particular platform
    if "linux" in sys.platform:
        # linux
        maud_exc = os.path.join(file_path, 'resources', 'maud_linux.sh')
    elif "darwin" in sys.platform:
        # OS X
        maud_exc = os.path.join(file_path, 'resources', 'maud_osx.sh')
    elif "win" in sys.platform:
        # Windows...
        maud_exc = os.path.join(file_path, 'resources', 'maud_win.bat')
    else:
        raise Exception(f"Supported platforms are linux, darwin (mac), and win.")

    # Check if executable does not exists else return maud_exc
    if not os.path.isfile(maud_exc):
        raise FileNotFoundError(errno.ENOENT,
                                os.strerror(errno.ENOENT),
                                maud_exc)
    return maud_exc
