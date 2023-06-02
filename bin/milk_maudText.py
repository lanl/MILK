#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 14:46:59 2022

@author: danielsavage
"""

import MILK
import os
import argparse


def main():
    """Run user supplied ins commandline."""
    parser = argparse.ArgumentParser(
        description="Run MAUD ins file.")
    parser.add_argument("-f", "--file", type=str, required=True,
                        help="Ins filename and relative path.")
    parser.add_argument("-p", "--maud_path", type=str, default=None,
                        help="Path to MAUD installation if different than MAUD_PATH in environement.")
    parser.add_argument("-j", "--java_opt", type=str, default="mx8G",
                        help="Java commandline options.")
    args = parser.parse_args()

    if args.maud_path is None:
        args.maud_path = os.getenv('MAUD_PATH')

    MILK.MAUDText.callMaudText.run_MAUD(
        args.maud_path,
        args.java_opt,
        'True',
        None,
        args.file
    )


if __name__ == "__main__":
    main()
