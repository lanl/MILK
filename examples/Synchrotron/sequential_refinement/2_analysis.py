#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 16:47:10 2021

@author: danielsavage
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" 
Created on Sun Jan 24 19:57:30 2021

@author: danielsavage
"""


import MILK
if __name__ == '__main__':
    # Initialize environment
    #===================================================#
    config = MILK.load_json('milk.json')
    dataset = MILK.load_json('dataset.json')

    editor = MILK.parameterEditor.editor()
    editor.parseConfig(config)
    maudText = MILK.maud.maudText()
    maudText.parseConfig(config)
    #===================================================#

    # Setup phase fractions based on preidentified regions
    #===================================================#
    p = ['alpha', 'steel', 'beta']
    editor.set_val(key='_pd_phase_atom_', value='0.33')
    editor.fix(key='_pd_phase_atom_')

    editor.wild_range = [[]]
    no_beta = list(range(0, 4))
    for wild in no_beta:
        editor.set_val(key='_pd_phase_atom_', loopid='0', value='0.5', wild=[wild])
        editor.set_val(key='_pd_phase_atom_', loopid='1', value='0.5', wild=[wild])
        editor.set_val(key='_pd_phase_atom_', loopid='2', value='0.0', wild=[wild])

    no_alpha = list(range(9, 19))
    for wild in no_alpha:
        editor.set_val(key='_pd_phase_atom_', loopid='0', value='0.0', wild=[wild])
        editor.set_val(key='_pd_phase_atom_', loopid='1', value='0.5', wild=[wild])
        editor.set_val(key='_pd_phase_atom_', loopid='2', value='0.5', wild=[wild])

    # Sequential copy lattice parameters based on phase regions
    #===================================================#
    maudText.wild_range = [[]]
    for wild in reversed(range(0, 27)):
        editor.get_val(key='cell_length_a', wild=[wild+1])
        a = editor.value
        editor.get_val(key='cell_length_c', wild=[wild+1])
        c = editor.value
        editor.set_val(key='cell_length_a', value=a[0], sobj=p[0], wild=[wild])
        editor.set_val(key='cell_length_c', value=c[0], sobj=p[0])
        editor.set_val(key='cell_length', value=a[1], sobj=p[1])
        editor.set_val(key='cell_length', value=a[2], sobj=p[2])

        if wild not in no_alpha:
            editor.free(key='cell_length_a', sobj=p[0])
            editor.free(key='cell_length_c', sobj=p[0])

        editor.free(key='cell_length_a', sobj=p[1])

        if wild not in no_beta:
            editor.free(key='cell_length_a', sobj=p[2])

        nback_add = 4
        for _ in range(0, nback_add):
            editor.add(key='_riet_par_background_pol', nsobj='chi(')  # Add shared background only
        editor.free(key='Background')
        maudText.wild = [wild]
        maudText.refinement(itr='4', ifile=editor.ifile, inc_step=False)

    # Consolodate results, add backgrouind, refine phases and further refine step 1 in parallel
    #===============================================================#
    for wild in range(0, 28):
        editor.free(key='_pd_phase_atom_', wild=[wild])
        if wild in no_alpha:
            editor.fix(key='_pd_phase_atom_', loopid='0')
        elif wild in no_beta:
            editor.fix(key='_pd_phase_atom_', loopid='2')

    maudText.wild = []
    maudText.wild_range = [[0, 27]]
    maudText.refinement(itr='8', ifile=editor.ifile)

    # Free texture and broadening if phase fraction isn't too small
    #===================================================#
    for wild in range(0, 28):
        editor.get_val(key='_pd_phase_atom_', wild=[wild])
        for i, vol in enumerate(editor.value):
            if float(vol) > 0.01:
                editor.free(key='_rita_harmonic_parameter', sobj=p[i])
                editor.free(key='MicroStrain', sobj=p[i])
                editor.free(key='CrystSize', sobj=p[i])

    maudText.refinement(itr='8', export_plots=True, ifile=editor.ifile, ofile='After_seq.par')
