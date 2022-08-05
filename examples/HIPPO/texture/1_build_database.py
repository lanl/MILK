#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 24 19:57:30 2021

@author: danielsavage
"""

import MILK
import glob
import numpy as np


def get_data(data_path, ext):
    """Walk the data directory looking for files with the data ext."""
    files = list(set(glob.glob(data_path+'*'+ext)))
    return [file.replace(data_path, "") for file in files]


def group_data(data_files, groupsz):
    """Group data by group size assuming increasing run number."""
    data_files.sort()
    return np.reshape(data_files, (-1, groupsz))


if __name__ == '__main__':

    # import config files
    #===================================================#
    dataset = MILK.load_json('dataset.json')
    config = MILK.load_json('milk.json')

    # Format input into an (analysis x rotation) numpy array
    #===================================================#
    data_files = get_data(dataset["data_dir"], dataset["data_ext"])
    data_files = group_data(data_files, dataset["data_group_size"])

    # Use generateGroup class to build the dataset and setup the parameter file
    #===================================================#
    group = MILK.generateGroup.group()
    group.parseConfig(
        config,
        dataset,
        data_fnames=data_files,
        ifile=dataset["template_name"],
        ofile=config["ins"]["riet_analysis_file"])
    group.writeDataset()
    group.prepareData()
