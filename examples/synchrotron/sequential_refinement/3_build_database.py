#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 21:59:58 2022

@author: danielsavage
"""
import MILK
import pandas as pd

if __name__ == '__main__':

    # Initialize environment
    #===================================================#
    config = MILK.load_json('milk.json')

    editor = MILK.parameterEditor.editor()
    editor.parseConfig(config, ifile="After_seq.par")

    #===================================================#

    db = {}

    phases = ['alpha', 'steel', 'beta']
    # Set the parameters to a reasonable estimates
    #===================================================#
    # Start nontexture background + scale #make sure it works on 0 and 24 using MILK
    wilds = range(editor.wild_range[0][0], editor.wild_range[0][1]+1)
    editor.wild_range = [[]]
    for i, phase in enumerate(phases):

        db[f'{phase}_lattice_a'] = []
        db[f'{phase}_lattice_a_err'] = []
        if i == 0:
            db[f'{phase}_lattice_c'] = []
            db[f'{phase}_lattice_c_err'] = []
        db[f'{phase}_atom_frac'] = []

        for wild in wilds:
            editor.get_val(key='_cell_length_a', sobj=phase, wild=[wild])
            db[f'{phase}_lattice_a'].append(float(editor.value[0]))

            editor.get_err(key='_cell_length_a', sobj=phase, wild=[wild])
            db[f'{phase}_lattice_a_err'].append(float(editor.value[0]))

            if i == 0:
                editor.get_val(key='_cell_length_c', sobj=phase, wild=[wild])
                db[f'{phase}_lattice_c'].append(float(editor.value[0]))

                editor.get_err(key='_cell_length_c', sobj=phase, wild=[wild])
                db[f'{phase}_lattice_c_err'].append(float(editor.value[0]))

            editor.get_val(key='_pd_phase_atom_', loopid=str(i), wild=[wild])
            db[f'{phase}_atom_frac'].append(float(editor.value[0]))

    db['Rwp'] = []
    db['Rexp'] = []
    db['GOF'] = []
    for wild in wilds:
        editor.get_val(key='_refine_ls_wR_factor_all', wild=[wild])
        db['Rwp'].append(float(editor.value[0]))

        editor.get_val(key='_refine_ls_goodness_of_fit_all', wild=[wild])
        db['Rexp'].append(float(editor.value[0]))

        db['GOF'].append(db['Rwp'][-1]/db['Rexp'][-1])

    df = pd.DataFrame.from_dict(db, orient='index').transpose()
    df.to_csv('milk_db.csv')
