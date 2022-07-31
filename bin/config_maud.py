#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 11:11:33 2022

@author: danielsavage
"""
import os
import sys
import argparse

conda_prefix = os.getenv('CONDA_PREFIX')


def bash_install(maud_path):
    """Configure conda environment initializers to have MAUD_PATH."""
    fname_act = os.path.join(conda_prefix, "etc/conda/activate.d")
    os.makedirs(fname_act, exist_ok=True)
    lines = ['#!/bin/bash', '', 'export MAUD_PATH='+maud_path]
    write_lines(os.path.join(fname_act, "env_vars.sh"), lines)

    fname_deact = os.path.join(conda_prefix, "etc/conda/deactivate.d")
    os.makedirs(fname_deact, exist_ok=True)
    lines = ['#!/bin/bash', '', 'unset MAUD_PATH']
    write_lines(os.path.join(fname_deact, "env_vars.sh"), lines)


def bat_install(maud_path):
    """Configure conda environment initializers to have MAUD_PATH."""
    fname_act = os.path.join(conda_prefix, "etc/conda/activate.d")
    os.makedirs(fname_act, exist_ok=True)
    lines = [f"set MAUD_PATH='{maud_path}'"]
    write_lines(os.path.join(fname_act, "env_vars.sh"), lines)

    fname_deact = os.path.join(conda_prefix, "etc/conda/deactivate.d")
    os.makedirs(fname_deact, exist_ok=True)
    lines = ["set MAUD_PATH="]
    write_lines(os.path.join(fname_deact, "env_vars.sh"), lines)


def write_lines(fname, lines):
    """Write a list of lines to a file."""
    with open(fname, 'w') as f:
        for line in lines:
            f.write(line+'\n')


def main():
    """Get user supplied MAUD path and add to conda milk env."""
    parser = argparse.ArgumentParser(
        description="Install MAUD to path from installation path given by user.")
    parser.add_argument("-p", "--maud_path", type=str, default=None,
                        help="Full path to MAUD installation.")
    args = parser.parse_args()

    if "linux" in sys.platform or "darwin" in sys.platform:
        bash_install(args.maud_path)

    elif "win" in sys.platform:
        # TODO Verify the windows installation works
        bat_install(args.maud_path)

    else:
        raise OSError("Unsupported OS for automated MAUD installation")


if __name__ == "__main__":
    main()
