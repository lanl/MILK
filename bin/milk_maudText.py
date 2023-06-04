#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 14:46:59 2022

@author: danielsavage
"""

from MILK.MAUDText import callMaudText
from os import getenv
import argparse
from pathlib import Path


def main():
    """Run user supplied ins commandline."""
    parser = argparse.ArgumentParser(
        description="Run MAUD ins file.")
    parser.add_argument("-f", "--file", type=str, required=True,
                        help="Ins filename and relative path.")
    parser.add_argument("-p", "--maud_path", type=str, default=getenv('MAUD_PATH').strip("'"),
                        help="Path to MAUD installation if different than MAUD_PATH in environement.")
    parser.add_argument("-j", "--java_opt", type=str, default="mx8G",
                        help="Java commandline options.")
    parser.add_argument("-s", "--simple_call", action='store_true',
                        help="If specified no log files are output.")
    parser.add_argument("-t", "--timeout", type=float, default=None,
                        help="Sets maximum time in seconds for MAUD to run.")
    args = parser.parse_args()

    callMaudText.run_MAUD(
        args.maud_path,
        args.java_opt,
        str(args.simple_call),
        args.timeout,
        args.file)


if __name__ == "__main__":
    main()
