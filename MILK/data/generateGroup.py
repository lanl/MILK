#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 14:38:43 2020

@author: danielsavage
"""
import os
import argparse
from . import prepareData
import pandas as pd
from pathlib import Path

class group:
    def __init__(self):
        self.filename = None
        self.run_dirs = None
        self.ifile = None
        self.ofile = None
        self.data_dir = None
        self.ext = None
        self.args = None
        self.data_fnames = None
        self.overwrite = False

    def parseConfig(self, config, dataset, data_fnames=None, run_dirs=None, ifile=None, ofile=None, data_dir=None, ext=None, filename='dataset.csv'):

        if run_dirs is None:
            self.run_dirs = config["folders"]["run_dirs"]
        else:
            self.run_dirs = run_dirs

        if ifile is None:
            self.ifile = config["ins"]["riet_analysis_file"]
        else:
            self.ifile = ifile

        if ofile is None:
            self.ofile = config["ins"]["riet_analysis_fileToSave"]
        else:
            self.ofile = ofile

        if data_dir is None:
            self.data_dir = dataset["data_dir"]
        else:
            self.data_dir = data_dir

        if data_fnames is None:
            self.data_fnames = dataset["data_fnames"]
        else:
            self.data_fnames = data_fnames

        if ext is None:
            self.ext = dataset["data_ext"]
        else:
            self.ext = ext

        self.filename = filename
        self.nruns = len(self.data_fnames)

    def buildDataset(self, zfilnum=3):
        self.dataset = {"run":[],"data_dir":[],"folder":[],"ifile":[],"ofile":[],"data_files":[]}
        for i, data_files in enumerate(self.data_fnames):
            folder = self.run_dirs.replace('(wild)', str(i).zfill(zfilnum))
            self.dataset["run"].append(True)
            self.dataset["data_dir"].append(self.data_dir)
            self.dataset["folder"].append(folder)
            self.dataset["ifile"].append(self.ifile)
            self.dataset["ofile"].append(self.ofile)
            self.dataset["data_files"].append(data_files)

    def writeDataset(self, work_dir = Path.cwd()):
        """Write dataset file for editing"""
        filename = work_dir / Path(self.filename)
        if not os.path.isfile(filename) or self.overwrite:
            df = pd.DataFrame.from_dict(self.dataset, orient='index').transpose()
            df.to_csv(filename, index=False)
        else:
            print()

    def prepareData(self, work_dir = Path.cwd(), keep_intensity=True):
        prepareData.main(filename = work_dir / Path(self.filename), keep_intensity=keep_intensity)
            