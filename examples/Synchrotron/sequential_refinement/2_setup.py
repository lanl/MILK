#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import MILK
import pandas as pd
import build_cinema_database
from pathlib import Path
import copy


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

    editor = MILK.parameterEditor.editor()
    editor.parseConfig(config)
    maudText = MILK.maud.maudText()
    maudText.parseConfig(config)

    df = pd.read_csv("dataset.csv")
    dataset = df.to_dict(orient='list')
    set_dataset_wild(dataset["run"], editor, maudText)

    # Use MAUD to load the phases (or not)
    #============================================================#
    # editor.fix_all()
    # maudText.refinement(itr='1',ifile=editor.ifile,inc_step=False,simple_call=True)

    # Set user parameters from dataset.csv (or not)
    #============================================================#
    # editor.ifile = set_dataset_starting_values(editor, dataset, config_dataset)

    # Ensure backgrounds are reset, refine intensities, and export plots
    #============================================================#
    editor.free(key='Background')
    editor.free(key='_pd_proc_intensity_incident')
    maudText.refinement(itr='3', export_plots=True, ifile=editor.ifile, ofile='After_setup.par')

    # Build the cinema database and visualize
    #============================================================#
    # build_cinema_database.main()
    # MILK.cinema.main()
