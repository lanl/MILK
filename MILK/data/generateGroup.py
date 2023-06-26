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
        self.zfill = None

    def parseConfig(self, config, dataset, data_fnames=None, run_dirs=None, ifile=None, ofile=None, data_dir=None, ext=None, zfill=3, filename='dataset.csv'):
        self.run_dirs = config["folders"]["run_dirs"] if run_dirs is None else run_dirs
        self.ifile = config["ins"]["riet_analysis_file"] if ifile is None else ifile
        self.ofile = config["ins"]["riet_analysis_fileToSave"] if ofile is None else ofile
        self.data_dir = dataset["data_dir"] if data_dir is None else data_dir
        self.data_fnames = dataset["data_fnames"] if data_fnames is None else data_fnames
        self.ext = dataset["data_ext"] if ext is None else ext
        self.zfill = config["folders"]["zfill"] if zfill is None else zfill
        if "zfill" in config["folders"].keys():
            self.zfill = config["folders"]["zfill"] if config["folders"]["zfill"] is not None else zfill
        else:
            self.zfill = zfill
        self.filename = filename
        self.nruns = len(self.data_fnames)

    def buildDataset(self):
        self.dataset = {"run":[],"data_dir":[],"folder":[],"ifile":[],"ofile":[],"data_files":[]}
        for i, data_files in enumerate(self.data_fnames):
            folder = self.run_dirs.replace('(wild)', str(i).zfill(self.zfill))
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
            