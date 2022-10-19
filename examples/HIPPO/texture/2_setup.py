#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import MILK
import pandas as pd
import build_cinema_database
from pathlib import Path
import copy

def free_bank_parameters(keyname, editor, hippo):
    for detid, bankRange in enumerate(hippo["banks"]):
        detector = hippo["detectors"][detid]
        for i in range(bankRange[0], bankRange[1]):
            if i+1 not in hippo["banks_remove"]:
                editor.free(key=keyname, sobj=f'{hippo["bank_prefix"]}{detector}', loopid=str(i))
    return editor

def fix_bank_parameters(keyname, editor, hippo):
    for detid, bankRange in enumerate(hippo["banks"]):
        detector = hippo["detectors"][detid]
        for i in range(bankRange[0], bankRange[1]):
            editor.fix(key=keyname, sobj=f'{hippo["bank_prefix"]}{detector}', loopid=str(i))
    return editor

def configure_hippo_parameters(editor, hippo) -> MILK.parameterEditor.editor:
    """Do standard HIPPO parameter setup."""
    # For HIPPO data don't store the spectra in the parameter file
    editor.set_val(key='_maud_store_spectra_with_analysis', value='false')

    # Set the dataset sample rotation angles
    for i, rot_name in enumerate(hippo["rot_names"]):
        editor.set_val(key='_pd_meas_angle_omega', value=str(hippo["omega_meas"][i]), sobj=rot_name)
        editor.set_val(key='_pd_meas_angle_chi', value=str(hippo["chi_meas"][i]), sobj=rot_name)
        editor.set_val(key='_pd_meas_angle_phi', value=str(hippo["phi_meas"][i]), sobj=rot_name)

    # Apply the sample rotations (e.g. to align sample axis in PFs)
    editor.set_val(key='_pd_spec_orientation_omega', value=str(hippo["omega_samp"]), sobj='First')
    editor.set_val(key='_pd_spec_orientation_chi', value=str(hippo["chi_samp"]), sobj='First')
    editor.set_val(key='_pd_spec_orientation_phi', value=str(hippo["phi_samp"]), sobj='First')

    # Remove banks
    for i, bankid in enumerate(hippo["banks_remove"]):
        editor.set_val(key='_riet_meas_datafile_compute', value='false',
                       sobj='gda('+str(bankid)+')')  # move bank list to input

    # Set the d-spacing
    for i, dspacing in enumerate(hippo["dspacing"]):
        editor.set_val(key='_pd_proc_2theta_range_min',
                       value=str(dspacing[0]),
                       sobj=f'{hippo["bank_prefix"]}{hippo["detectors"][i]}')
        editor.set_val(key='_pd_proc_2theta_range_max',
                       value=str(dspacing[1]),
                       sobj=f'{hippo["bank_prefix"]}{hippo["detectors"][i]}')

    # Fix one difc to break lattice parameter correlation
    editor.get_val(key='_instrument_bank_difc',
                   loopid='0',
                   sobj=f'{hippo["bank_prefix"]}{hippo["detectors"][0]} {hippo["rot_names"][0]}',
                   nsobj='90.0')

    editor.ref(key1='_instrument_bank_difc',
               key2='_pd_spec_size_radius_y',
               value=f'{editor.value[0]} 0 100000',
               loopid='0',
               sobj1=f'{hippo["bank_prefix"]}{hippo["detectors"][0]} {hippo["rot_names"][0]}',
               nsobj1='90.0')

    return editor

def set_dataset_starting_values(editor,dataset,config_dataset) -> str:
    """Apply the dataset phase initialization keys"""
    # Deep copy the editor object so no changes to editor leave this function
    editor = copy.deepcopy(editor)
    ifile = editor.ifile
    ofile = editor.ofile
    work_dir = editor.work_dir
    editor.work_dir=''
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
                editor.set_val(key=f"{key}",value=f"{value}",sobj=phase_name,use_stored_par=True)
        editor.write_par()

    return ofile

def set_dataset_wild(run,editor,maudText):
    """"""
    wild = [i for i, x in enumerate(run) if x]
    editor.wild=wild
    maudText.wild=wild

if __name__ == '__main__':

    # Initialize environment
    #===================================================#
    config = MILK.load_json('milk.json')
    config_hippo = MILK.load_json('hippo.json')
    config_dataset = MILK.load_json('dataset.json')

    editor = MILK.parameterEditor.editor()
    editor.parseConfig(config)
    maudText = MILK.maud.maudText()
    maudText.parseConfig(config)

    df = pd.read_csv("dataset.csv")
    dataset = df.to_dict(orient='list')
    set_dataset_wild(dataset["run"],editor,maudText)
    #===================================================#

    # Configure the hippo parameters and ensure all parameters are fixed
    #============================================================#
    editor.fix_all()
    editor = configure_hippo_parameters(editor, config_hippo)

    # Use MAUD to load the phases
    #============================================================#
    maudText.refinement(itr='1', import_phases=True, ifile=editor.ifile,inc_step=False,simple_call=True)

    # Set user parameters from dataset.csv
    #============================================================#
    editor.ifile = set_dataset_starting_values(editor,dataset,config_dataset)

    # Refine intensities and export plots
    #============================================================#
    editor = free_bank_parameters('_inst_inc_spectrum_scale_factor', editor, config_hippo)
    maudText.refinement(itr='3', export_plots=True,ifile=editor.ifile, 
                        ofile='After_setup.par',inc_step=True,simple_call=False)

    # Build the cinema database and visualize
    #============================================================#
    build_cinema_database.main()
    MILK.cinema.main()