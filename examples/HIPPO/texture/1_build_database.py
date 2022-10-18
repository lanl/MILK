#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import MILK
import numpy as np


def get_data(data_path: str, ext: str) -> list:
    """Walk the data directory looking for files with the data ext."""
    files = Path(data_path).glob(f"*{ext}")
    return sorted([file.name for file in files])

def group_data(data_files: list, groupsz: int) -> list:
    """Group data by group size assuming increasing run number."""
    data_files.sort()
    return np.reshape(data_files, (-1, groupsz))

def user_data(ds: dict, n_run: int, config: dict) -> dict:
    """Add user data from dataset.json to a dataset with n_runs."""
    # metadata
    for key,val in config["meta_data"].items():
        ds[key] = val

    # Add phase parameters to initialize
    for key,vals in config["phase_initialization"].items():
        for i, val in enumerate(vals):
            ds[f"{key}_{i}"] = [val]*n_run
    
    # Validate the dictionary
    for key,val in ds.items():
        assert len(val)==n_run, f"Error: key: {key} has length: {len(val)} but should be length: {n_run}"

    return ds

if __name__ == '__main__':

    # import config files
    #===================================================#
    config_dataset = MILK.load_json('dataset.json')
    config = MILK.load_json('milk.json')

    # Format input into an (analysis x rotation) numpy array
    #===================================================#
    data_files = get_data(config_dataset["data_dir"], config_dataset["data_ext"])
    data_files = group_data(data_files, config_dataset["data_group_size"])

    # Use generateGroup class to build the dataset and setup the parameter file
    #===================================================#
    group = MILK.generateGroup.group()
    group.parseConfig(
        config,
        config_dataset,
        data_fnames=data_files,
        ifile=config_dataset["template_name"],
        ofile=config["ins"]["riet_analysis_file"])
    group.buildDataset()
    group.dataset = user_data(group.dataset, group.nruns, config_dataset)
    group.writeDataset()
    group.prepareData(keep_intensity=False)
