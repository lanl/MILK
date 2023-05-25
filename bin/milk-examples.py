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
            3. Synchrotron XRD analysis. 4. CHESS: GE Detector calibration and integration. 5. APS 1D Hydra 4 detector calibration.")
    args = parser.parse_args()

    args.maud_path = os.getenv('MAUD_PATH')

    if args.example == 1:
        MILK.examples.maudBatch()
    elif args.example == 2:
        MILK.examples.hippoTexture()
    elif args.example == 3:
        MILK.examples.sequentialRefinement()
    elif args.example == 4:
        MILK.examples.GEDetector()
    elif args.example == 5:
        MILK.examples.APSHydra()
    else:
        raise OSError("Use command milk-examples.py -e n to setup a tutorial where n is one of the valid examples. See milk-examples.py -h for a list.")


if __name__ == "__main__":
    main()
