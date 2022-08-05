#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 14:38:43 2020

@author: danielsavage
"""
import os
import argparse
from . import prepareData


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

    def parseConfig(self, config, dataset, data_fnames=None, run_dirs=None, ifile=None, ofile=None, data_dir=None, ext=None, filename='groupDatasets.txt'):

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

    def writeDataset(self, zfilnum=3):
        """Write dataset file for editing"""
        fname = os.path.abspath(self.filename)
        with open(fname, "w") as f:
            # write cif loop header
            f.write('DataDir RunDir template.par output.par dataset1 dataset2 datasets3...\n')
            for i, data_fname in enumerate(self.data_fnames):
                folder = self.run_dirs.replace('(wild)', str(i).zfill(zfilnum))
                f.write(f"{self.data_dir} {folder} {self.ifile} {self.ofile} ")
                for file in data_fname:
                    f.write(f"{file} ")
                f.write('\n')

    def prepareData(self):
        prepareData.main('-fn '+self.filename)
