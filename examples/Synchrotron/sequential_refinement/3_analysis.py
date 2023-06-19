#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import MILK
import pandas as pd
import build_cinema_database
from pathlib import Path
import copy
from tqdm import tqdm


def set_dataset_starting_values(editor, dataset, config_dataset) -> str:
    """Apply the dataset phase initialization from the config_dataset keys."""
    # Deep copy the editor object so no changes to editor leave this function
    editor = copy.deepcopy(editor)
    ifile = editor.ifile
    ofile = editor.ofile
    work_dir = editor.work_dir
    editor.work_dir = ''
    for datasetid, folder in enumerate(dataset["folder"]):
        file_path = Path(work_dir) / folder
        editor.ifile = str(file_path / ifile)
        editor.ofile = str(file_path / ofile)
        editor.read_par()
        editor.get_phases(use_stored_par=True)
        phase_names = editor.value
        for key in config_dataset["phase_initialization"].keys():
            for phaseid, phase_name in enumerate(phase_names):
                value = dataset[f"{key}_{phaseid}"][datasetid]
                if "_pd_phase_atom_" in key:
                    editor.set_val(
                        key=f"{key}", value=f"{value}", loopid=f"{phaseid}", use_stored_par=True)
                else:
                    editor.set_val(
                        key=f"{key}", value=f"{value}", sobj=phase_name, use_stored_par=True)
        editor.write_par()

    return ofile


def set_dataset_wild(run, editor, maudText):
    """From locical run array build wild."""
    wild = [i for i, x in enumerate(run) if x]
    editor.wild = wild
    maudText.wild = wild


if __name__ == '__main__':
    # Initialize environment
    #===================================================#
    config = MILK.load_json('milk.json')
    config_dataset = MILK.load_json('dataset.json')
    df = pd.read_csv("dataset.csv")
    dataset = df.to_dict(orient='list')

    editor = MILK.parameterEditor.editor()
    editor.parseConfig(config, ifile='After_setup.par')
    maudText = MILK.maud.maudText()
    maudText.parseConfig(config, cur_step=2)
    #===================================================#

    # Set user parameters from dataset.csv (or not)
    #============================================================#
    set_dataset_wild(dataset["run"], editor, maudText)
    # editor.ifile = set_dataset_starting_values(editor, dataset, config_dataset)

    # Setup phase fractions based on preidentified regions
    #===================================================#
    p = {'alpha': '0', 'steel':'1', 'beta':'2'}
    editor.set_val(key='_pd_phase_atom_', value='0.33')
    editor.fix(key='_pd_phase_atom_')

    no_beta = list(range(0, 4))
    for wild in no_beta:
        editor.set_val(key='_pd_phase_atom_', loopid=p['alpha'],
                       value='0.5', wild=[wild])
        editor.set_val(key='_pd_phase_atom_', loopid=p['steel'],
                       value='0.5', wild=[wild])
        editor.set_val(key='_pd_phase_atom_', loopid=p['beta'],
                       value='0.0', wild=[wild])

    no_alpha = list(range(9, 19))
    for wild in no_alpha:
        editor.set_val(key='_pd_phase_atom_', loopid=p['alpha'],
                       value='0.0', wild=[wild])
        editor.set_val(key='_pd_phase_atom_', loopid=p['steel'],
                       value='0.5', wild=[wild])
        editor.set_val(key='_pd_phase_atom_', loopid=p['beta'],
                       value='0.5', wild=[wild])

    # Add shared background and free 
    #===================================================#
    set_dataset_wild(dataset["run"], editor, maudText)
    for _ in range(0, 4):
        editor.add_loop_par(key='_riet_par_background_pol',
                            nsobj='chi(')  # Add shared background only
    editor.free(key='Background')

    # Sequential copy lattice parameters based on phase regions
    #===================================================#
    print("Starting sequential fit ...")
    wild_prev = editor.wild[-1]
    for wild in tqdm(reversed(editor.wild), total=len(editor.wild)):
        # Copy lattice parameters from previous
        editor.get_val(key='cell_length_a', wild=[wild_prev])
        a = editor.value
        editor.get_val(key='cell_length_c', wild=[wild_prev])
        c = editor.value
        editor.set_val(key='cell_length_a', value=a[int(p['alpha'])], sobj='alpha', wild=[wild])
        editor.set_val(key='cell_length_c', value=c[int(p['alpha'])], sobj='alpha')
        editor.set_val(key='cell_length', value=a[int(p['steel'])], sobj='steel')
        editor.set_val(key='cell_length', value=a[int(p['beta'])], sobj='beta')

        # Free phase fractions and refine
        editor.free(key='_pd_phase_atom_', wild=[wild])
        if wild in no_alpha:
            editor.fix(key='_pd_phase_atom_', loopid=p['alpha'])
        elif wild in no_beta:
            editor.fix(key='_pd_phase_atom_', loopid=p['beta'])

        maudText.wild = [wild]
        maudText.refinement(itr='4', ifile=editor.ifile,
                            inc_step=False, simple_call=True)

        # Conditionally free lattice parameters and refine
        if wild not in no_alpha:
            editor.free(key='cell_length_a', sobj='alpha')
            editor.free(key='cell_length_c', sobj='alpha')

        editor.free(key='cell_length_a', sobj='steel')

        if wild not in no_beta:
            editor.free(key='cell_length_a', sobj='beta')
        
        maudText.refinement(itr='6', ifile=editor.ifile,
                            inc_step=False, simple_call=True)
        
        #Set previous to current wild for sequential copy
        wild_prev = wild

    # Step 2: Consolodate results and refine step 2 in parallel
    #===============================================================#
    set_dataset_wild(dataset["run"], editor, maudText)
    maudText.refinement(itr='8', ifile=editor.ifile,
                        inc_step=True, export_plots=True)

    # Step 3: Free texture and broadening if phase fraction isn't too small
    #===================================================#
    for wild in editor.wild:
        editor.get_val(key='_pd_phase_atom_', wild=[wild])
        for vol,pname in zip(editor.value,p.keys()):
            if float(vol) > 0.01:
                editor.free(key='_rita_harmonic_parameter', sobj=pname)
                editor.free(key='MicroStrain', sobj=pname)
                editor.free(key='CrystSize', sobj=pname)

    maudText.refinement(itr='8', export_plots=True,
                        ifile=editor.ifile, ofile='After_seq.par')

    # Build the cinema database and visualize
    #============================================================#
    build_cinema_database.main()
    MILK.cinema.main()
