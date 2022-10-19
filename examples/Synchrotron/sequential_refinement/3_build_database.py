#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 21:59:58 2022

@author: danielsavage
"""
import MILK
import pandas as pd
import os
from numpy import NAN


def sync_length(db, cur_index):
    for key, val in db.items():
        while len(val) < cur_index:
            db[key].append(NAN)
    return db


def get_files(target_file, head_directory):
    files, paths = MILK.utilities.search(keyword=target_file,
                                         directory=head_directory, exact=False)
    dic = {}
    for f, p in zip(files, paths):

        if p in dic.keys():
            dic[p].append(f)
        else:
            dic[p] = [f]

    files = []
    file_paths = []
    for key, val in dic.items():
        # Construct the list of data based on gda
        files.append(val)
        file_paths.append(key)

    return files, file_paths


if __name__ == '__main__':

    # Initialize environment
    #===================================================#
    config = MILK.load_json('milk.json')

    editor = MILK.parameterEditor.editor()
    editor.parseConfig(config, ifile="After_seq.par", wild=[0], wild_range=[[]])
    #===================================================#

    files, file_paths = get_files("plot1d_detector1.png", os.getcwd())

    # Build database
    #===================================================#
    keys = {
        "Rwp": {"key": "_refine_ls_wR_factor_all", "sobj": None, "isloop": False},
        "Rexp": {"key": "_refine_ls_goodness_of_fit_all", "sobj": None, "isloop": False},
        "phase_fraction": {"key": "_pd_phase_atom_", "sobj": None, "isloop": True},
        "Biso": {"key": "Biso", "sobj": "phase", "isloop": False},
        "Cryst_Sz": {"key": "_riet_par_cryst_size", "sobj": "phase", "isloop": False},
        "Mu_strain": {"key": "_riet_par_rs_microstrain", "sobj": "phase", "isloop": False},
        "lattice_a": {"key": "_cell_length_a", "sobj": "phase", "isloop": False},
        "lattice_b": {"key": "_cell_length_b", "sobj": "phase", "isloop": False},
        "lattice_c": {"key": "_cell_length_c", "sobj": "phase", "isloop": False},
        "lattice_alpha": {"key": "_cell_angle_alpha", "sobj": "phase", "isloop": False},
        "lattice_beta": {"key": "_cell_angle_beta", "sobj": "phase", "isloop": False},
        "lattice_gamma": {"key": "_cell_angle_gamma", "sobj": "phase", "isloop": False},

    }
    exclude_err = ["Rwp", "Rexp"]
    db = {}
    db["index"] = []
    db["phase_name"] = []
    db["GOF"] = []
    for key in keys.keys():
        db[key] = []
        if key not in exclude_err:
            db[f'{key}_e'] = []

    cur_index = 0
    for idir, (file_path, images) in enumerate(zip(file_paths, files)):
        editor.run_dirs = os.path.relpath(file_path, os.getcwd())

        for i, _ in enumerate(editor.run_dirs.split(os.sep)):
            if f'folder_lvl{i}' not in db.keys():
                db[f'folder_lvl{i}'] = [NAN]*len(db["Rwp"])

        for i, _ in enumerate(images):
            if f'FILE{i}' not in db.keys():
                db[f'FILE{i}'] = [NAN]*len(db["Rwp"])

        editor.get_val(key='_pd_phase_name')
        phases = [phase.strip().strip('\'') for phase in editor.value]
        for iph, phase in enumerate(phases):
            db["phase_name"].append(phase)

            for key, val in keys.items():

                if val["sobj"] is not None and "phase" in val["sobj"]:
                    sobj = phase
                else:
                    sobj = val["sobj"]

                if val["isloop"]:
                    loopid = f"{iph}"
                else:
                    loopid = None

                editor.get_val(key=val["key"], sobj=sobj, loopid=loopid)
                db[key].append(float(editor.value[0]))
                if key not in exclude_err:
                    editor.get_err(key=val["key"], sobj=sobj, loopid=loopid)
                    db[f'{key}_e'].append(float(editor.value[0]))
                    if db[f'{key}_e'][-1] == 0.0:
                        db[f'{key}_e'][-1] = NAN

            db['GOF'].append(db['Rwp'][-1]/db['Rexp'][-1])

            for i, image in enumerate(images):
                db[f'FILE{i}'].append(os.path.join(editor.run_dirs, image))

            for i, folder_lvl in enumerate(editor.run_dirs.split(os.sep)):
                db[f'folder_lvl{i}'].append(folder_lvl)

            db["index"].append(idir)
            db = sync_length(db, cur_index)
            cur_index += 1
    df = pd.DataFrame.from_dict(db, orient='index').transpose()
    df.to_csv('data.csv', index=False, na_rep='NaN')

    print(os.path.relpath(os.path.abspath('./'),
          '/Users/danielsavage/Downloads/cinema_debye_scherrer-master/databases.json'))
