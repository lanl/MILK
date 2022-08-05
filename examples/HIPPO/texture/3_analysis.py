#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 16:47:10 2021

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
    editor.parseConfig(config, ifile='After_setup.par')
    maudText = MILK.maud.maudText()
    maudText.parseConfig(config, cur_step='2')
    #===================================================#

    phases = ['Iron - alpha', 'Iron - gamma']
    # Set the parameters to a reasonable estimates
    #===================================================#
    for i, phase in enumerate(phases):
        if i > 0:
            editor.ref(key1='Biso', key2='Biso', value='0 1 100000', sobj1=phases[0], sobj2=phase)
        else:
            editor.set_val(key='Biso', sobj=phase, value='0.6')
        editor.set_val(key='MicroStrain', sobj=phase, value='0.002')
        editor.set_val(key='CrystSize', sobj=phase, value='500')
        editor.set_val(key='_pd_phase_atom_', loopid=f'{i}', value='0.5')

    # Refinement Step2: refine intensity and Background
    #==========================================================================#
    nback_add = 2
    for _ in range(0, nback_add):
        editor.add(key='_riet_par_background_pol', nsobj='gda(')  # Add shared background only
    editor.free(key='Background')  # tied bk parameters are ignored
    maudText.refinement(itr='4', ifile=editor.ifile)

    # Refinement Step3: Allow arbitrary texture and basic lattice parameters
    # ===================================================#
    editor = fix_bank_parameters('_inst_inc_spectrum_scale_factor', editor, hippo)  # Refine Difc
    editor.free(key='_cell_length_a')
    editor.texture(key='Arbitrary')
    maudText.refinement(itr='3', ifile=editor.ifile)

    # Refinement Step4: Previous + difc
    #===================================================#
    editor.fix(key='_cell_length_a')
    editor = free_bank_parameters('_instrument_bank_difc', editor, hippo)  # Refine Difc
    maudText.refinement(itr='3', ifile=editor.ifile)

    # Refinement Step5: Previous + peak broadening
    #===================================================#
    editor.free(key='_cell_length_a')
    editor.free(key='MicroStrain')
    editor.free(key='CrystSize')
    maudText.refinement(itr='5', export_plots=True, ifile=editor.ifile)

    # Refinement Step6: Add EWIMV texture model and refine phase fractions
    #===================================================#
    editor.fix_all()
    editor.texture(key='EWIMV')
    editor.track(key='_rita_wimv_odf_coverage_')
    editor.set_val(key='_rita_wimv_iteration_max', value='15')
    editor.set_val(key='_rita_wimv_odf_resolution', value='7.5')
    editor.set_val(key='_rita_odf_refinable', value='true')
    editor.reset_odf()

    for i, phase in enumerate(phases):
        if i > 0:
            editor.free(key='_pd_phase_atom_', loopid=f'{i}')
    editor = free_bank_parameters('_inst_inc_spectrum_scale_factor', editor, hippo)
    maudText.refinement(itr='4', export_plots=True, ifile=editor.ifile)

    # Refinement Step7: Previous + Biso
    #=====================================================================#
    editor.free(key='Biso')
    maudText.refinement(itr='4', ifile=editor.ifile)

    # Refinement Step8: Previous + broadening + Background + cell
    #=====================================================================#
    editor.free(key='Background')
    editor.free(key='MicroStrain')
    editor.free(key='CrystSize')
    editor.free(key='_cell_length_a')
    maudText.refinement(itr='10', export_PFs=True,
                        export_plots=True, run=True, ofile="After_tex.par")
