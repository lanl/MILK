#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import MILK
import build_cinema_database
import time

def free_bank_parameters(keyname, editor, hippo):
    for detid, bankRange in enumerate(hippo["banks"]):
        detector = hippo["detectors"][detid]
        for i in range(bankRange[0], bankRange[1]):
            if i+1 not in hippo["banks_remove"]:
                editor.free(key=keyname, sobj='Bank'+str(detector), loopid=str(i))

def fix_bank_parameters(keyname, editor, hippo):
    for detid, bankRange in enumerate(hippo["banks"]):
        detector = hippo["detectors"][detid]
        for i in range(bankRange[0], bankRange[1]):
            editor.fix(key=keyname, sobj='Bank'+str(detector), loopid=str(i))

def bound_b_factors(editor):
    editor.ref(key1='Biso', key2='Biso', value='0 1 100000', nsobj1='First',sobj2='First')

def add_shared_background(nparameters,editor):
    for _ in range(0, nparameters):
        editor.add_loop_par(key='_riet_par_background_pol', nsobj='gda(')  # Add shared background only

def rem_shared_background(nparameters,editor):
    for _ in range(0, nparameters):
        editor.rem_loop_par(key='_riet_par_background_pol', nsobj='gda(')  # Add shared background only

def add_individual_background(nparameters,editor):
    for _ in range(0, nparameters):
        editor.add_datafile_bk_par()

def ref_individual_background(nparameters,editor):
    for _ in range(0, nparameters):
        editor.rem_loop_par(key='_riet_par_background_pol', sobj='gda(')  # Add shared background only

def free_scale_parameters(editor,hippo):
    editor.free(key='_pd_phase_atom_')
    editor.fix(key='_pd_phase_atom_',loopid='0')
    free_bank_parameters('_inst_inc_spectrum_scale_factor', editor, hippo)

def fix_scale_parameters(editor,hippo):
    editor.fix(key='_pd_phase_atom_')
    fix_bank_parameters('_inst_inc_spectrum_scale_factor', editor, hippo)

def free_microstructure(editor):
    editor.free(key='MicroStrain')
    editor.free(key='CrystSize')

def fix_microstructure(editor):
    editor.fix(key='MicroStrain')
    editor.fix(key='CrystSize')

def free_cell(editor):
    editor.free(key='_cell_length')
    editor.free(key='_cell_angle')

def fix_cell(editor):
    editor.fix(key='_cell_length')
    editor.fix(key='_cell_angle')

def free_difc(editor,hippo):
    editor = free_bank_parameters('_instrument_bank_difc', editor, hippo)  # Refine Difc

def fix_difc(editor,hippo):
    editor = fix_bank_parameters('_instrument_bank_difc', editor, hippo)  # Refine Difc

def set_EWIMV(editor,resolution: float = 7.5, iterations: int = 10, refineable: bool = True):
    editor.texture(key='EWIMV')
    editor.set_val(key='_rita_wimv_iteration_max', value=f"{iterations}")
    editor.set_val(key='_rita_wimv_odf_resolution', value=f"{resolution}")
    if refineable:
        editor.set_val(key='_rita_odf_refinable', value='true')
    else:
        editor.set_val(key='_rita_odf_refinable', value='false')

if __name__ == '__main__':
    start_time = time.time()

    # Initialize environment
    #===================================================#
    config = MILK.load_json('milk.json')
    config_hippo = MILK.load_json('hippo.json')

    editor = MILK.parameterEditor.editor()
    editor.parseConfig(config, ifile='After_setup.par')
    maudText = MILK.maud.maudText()
    maudText.parseConfig(config, cur_step='2')
    #===================================================#    

    # Refinement Step2: Tie biso, refine scale and Background
    bound_b_factors(editor)
    add_shared_background(2,editor)
    free_scale_parameters(editor,config_hippo)
    editor.free(key='Background')
    maudText.refinement(itr='4',  export_plots=True, ifile=editor.ifile)

    # Refinement Step3: Background, Arbitrary texture, lattice parameters
    fix_scale_parameters(editor,config_hippo)
    free_cell(editor)
    editor.texture(key='Arbitrary')
    maudText.refinement(itr='3', export_plots=True, ifile=editor.ifile)

    # Refinement Step4: Background, Arbitrary texture, and difc
    # fix_cell(editor)
    free_microstructure(editor)
    free_difc(editor,config_hippo)
    maudText.refinement(itr='6', export_plots=True, ifile=editor.ifile)

    # # Refinement Step5: Previous + cell parameters (note difc was fixed in setup)
    # free_cell(editor)
    # maudText.refinement(itr='3', export_plots=True, ifile=editor.ifile)

    # Refinement Step6: Add EWIMV texture model and refine phase fractions
    editor.fix_all()
    set_EWIMV(editor,resolution=7.5)
    free_scale_parameters(editor,config_hippo)    
    maudText.refinement(itr='4', export_PFs=True, export_plots=True, ifile=editor.ifile)

    # Refinement Step7: Previous + Biso
    editor.free(key='Biso')
    editor.free(key='Background')
    maudText.refinement(itr='4', export_PFs=True, export_plots=True,ifile=editor.ifile)

    # Refinement Step8: Previous + broadening + Background + cell
    free_microstructure(editor)
    free_cell(editor)
    maudText.refinement(itr='10', export_PFs=True,
                        export_plots=True, ofile="After_tex.par")

    # Build the cinema database and visualize
    build_cinema_database.main()
    print("--- %s seconds ---" % (time.time() - start_time))
    # MILK.cinema.main()