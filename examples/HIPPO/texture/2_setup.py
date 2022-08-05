#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 24 19:57:30 2021

@author: danielsavage
"""

import MILK


def free_bank_parameters(keyname, editor, hippo):
    for detid, bankRange in enumerate(hippo["banks"]):
        detector = hippo["detectors"][detid]
        for i in range(bankRange[0], bankRange[1]):
            if i+1 not in hippo["banks_remove"]:
                editor.free(key=keyname, sobj='Bank'+str(detector), loopid=str(i))
    return editor


def fix_bank_parameters(keyname, editor, hippo):
    for detid, bankRange in enumerate(hippo["banks"]):
        detector = hippo["detectors"][detid]
        for i in range(bankRange[0], bankRange[1]):
            editor.fix(key=keyname, sobj='Bank'+str(detector), loopid=str(i))
    return editor


if __name__ == '__main__':

    # Initialize environment
    #===================================================#
    config = MILK.load_json('milk.json')
    hippo = MILK.load_json('hippo.json')

    editor = MILK.parameterEditor.editor()
    editor.parseConfig(config)
    maudText = MILK.maud.maudText()
    maudText.parseConfig(config)
    #===================================================#

    # For HIPPO data don't store the spectra in the parameter file
    #===================================================#
    editor.set_val(key='_maud_store_spectra_with_analysis', value='false')

    # Set the dataset sample rotation angles
    #===================================================#
    for i, rot_name in enumerate(hippo["rot_names"]):
        editor.set_val(key='_pd_meas_angle_omega', value=str(hippo["omega_meas"][i]), sobj=rot_name)
        editor.set_val(key='_pd_meas_angle_chi', value=str(hippo["chi_meas"][i]), sobj=rot_name)
        editor.set_val(key='_pd_meas_angle_phi', value=str(hippo["phi_meas"][i]), sobj=rot_name)

    # Apply the sample rotations (e.g. to align sample axis in PFs)
    #===================================================#
    editor.set_val(key='_pd_spec_orientation_omega', value=str(hippo["omega_samp"]), sobj='First')
    editor.set_val(key='_pd_spec_orientation_chi', value=str(hippo["chi_samp"]), sobj='First')
    editor.set_val(key='_pd_spec_orientation_phi', value=str(hippo["phi_samp"]), sobj='First')

    # Remove banks
    #===================================================#
    for i, bankid in enumerate(hippo["banks_remove"]):
        editor.set_val(key='_riet_meas_datafile_compute', value='false',
                       sobj='gda('+str(bankid)+')')  # move bank list to input

    # Set the d-spacing
    #===================================================#
    for i, dspacing in enumerate(hippo["dspacing"]):
        editor.set_val(key='_pd_proc_2theta_range_min',
                       value=str(dspacing[0]),
                       sobj=str(hippo["detectors"][i]))
        editor.set_val(key='_pd_proc_2theta_range_max',
                       value=str(dspacing[1]),
                       sobj=str(hippo["detectors"][i]))

    # Fix one difc to break lattice parameter correlation
    #===================================================#
    editor.get_val(key='_instrument_bank_difc',
                   loopid='0',
                   sobj=f'Bank{hippo["detectors"][0]} {hippo["rot_names"][0]}',
                   nsobj='90.0')

    editor.ref(key1='_instrument_bank_difc',
               key2='_pd_spec_size_radius_y',
               value=f'{editor.value[0]} 0 100000',
               loopid='0',
               sobj1=f'Bank{hippo["detectors"][0]} {hippo["rot_names"][0]}',
               nsobj1='90.0')

    # Use MAUD to load the phase and refine the intensity scaling
    #============================================================#
    editor.fix_all()
    editor = free_bank_parameters('_inst_inc_spectrum_scale_factor', editor, hippo)
    maudText.refinement(itr='3', export_plots=True, import_phases=True,
                        ifile=editor.ifile, ofile='After_setup.par')
