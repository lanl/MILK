#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 23 16:13 2023

@author: ZhangxiFeng
"""

import MILK
import os
import argparse


def main():
    """Run user supplied ins commandline."""
    parser = argparse.ArgumentParser(
        description="Setup provided examples.")
    parser.add_argument("-e", "--example", type=int, required=True,
        help="Enter the number corresponding to the examples: 1. Maud batch processing. 2. HIPPO texture analysis. \
            3. Synchrotron XRD analysis. 4. CHESS: GE Detector calibration and integration.")
    args = parser.parse_args()

    args.maud_path = os.getenv('MAUD_PATH')

    if args.example == 1:
        MILK.examples.maudbatch()
    elif args.example == 2:
        MILK.examples.hippo_texture()
    elif args.example == 3:
        MILK.examples.sequential_refinement()
    elif args.example == 4:
        MILK.examples.GEDetector()
    else:
        raise OSError("Use command milk-examples.py -e n to setup a tutorial where n is either 1, 2, or 3")


if __name__ == "__main__":
    main()
