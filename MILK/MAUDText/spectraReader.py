#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed March 13 08:29:42 2024

@author: danielsavage
"""
from pathlib import Path
from MILK.parallel import parallel_map,get_ncpus
def read_spectra_cif(file):
    file_path = Path(file)
    assert file_path.is_file(), f"Parameter file <{file_path}> is not found on the absolute or relative path of the file"
    with open(file_path) as f:
        lines = f.readlines()
    return lines 

def parse_spectra(file):
    """Convert cif text representation to list of dictionary lists."""
    lines = read_spectra_cif(file)
    spectra = []
    for i,line in enumerate(lines):
        if "loop_" in line:
            ind = i + len(keys) + 1
            data = []
            for j in range(ind,ind+npoints):
                data.append([float(num) for num in lines[j].split(' ')[1:]])
            d={}
            for key,val in zip(keys,list(map(list, zip(*data)))):
                d[key]=val
            spectra.append(d)
            i = ind+npoints
        elif "_pd_meas_number_of_points" in line:
            npoints = int(line.split(" ")[1])
        elif "# On the following loop you will have:" in line:
            keys = lines[i+1].split('  ')[1:]
            for j,key in enumerate(keys): 
                if key=='':
                    keys.pop(j)
                else:
                    keys[j]=key.strip()

    return spectra

def extract_spectra(files,poolsize=get_ncpus()):
    return parallel_map(parse_spectra,poolsize,True,files)
