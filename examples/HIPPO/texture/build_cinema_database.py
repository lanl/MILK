#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import MILK
import pandas as pd
from pathlib import Path
from numpy import NAN

def tidy_dictionary(d: dict,length: int):
    """
    Formats all values and lists in dictionary to have
    len(length) and converts from dictionary of list to
    list of dictionary. 
    """
    for key, val in d.items():
        if isinstance(val,list):
            while len(val) < length:
                d[key].append(NAN)
        else:
            d[key]=[val]*length
    return [dict(zip(d,t)) for t in zip(*d.values())] 

def get_value(key,editor,loopid=None):
    """Wrapper for value error extraction from MAUD parameter file."""
    editor.get_val(key=key,loopid=loopid,use_stored_par=True)
    if editor.value==[]:
        return [NAN],[NAN]
    else:
        value = [float(value.strip()) for value in editor.value]
        editor.get_err(key=key,loopid=loopid,use_stored_par=True)
        error = [float(value.strip()) for value in editor.value]
        error = list(map(lambda x: x if (x!=0) else NAN, error))
        return value,error

def main():

    # Initialize environment
    #===================================================#
    config = MILK.load_json('milk.json')
    editor = MILK.parameterEditor.editor()
    editor.parseConfig(config,
                        run_dirs="",
                        wild=[0], 
                        wild_range=[[]])
    #===================================================#

    # Load run dataframe
    run_df = pd.read_csv("dataset.csv")
    run_include = ["folder","reduction_level"]

    # Initialize CINEMA output dictionary
    cinema_d = []

    # Loop over run names
    for run_index, run_folder in enumerate(run_df["folder"]):
        
        #Construct the full path to the run_name
        run_path = Path(run_folder)

        # Get list of MILK step folder paths in the run_folder
        step_paths = sorted(list(run_path.glob("step_*")))

        # For each step path
        for step_index, step_path in enumerate(step_paths):
            
            # Extract step_name from the path
            step_name = step_path.parts[-1]
            
            # Get png files and parameter (par) file
            png_files = list(step_path.glob("*.png"))
            par_files = list(step_path.glob("*.par"))
            editor.ifile = str(par_files[0])
            
            # Initialize step dictionary
            step_d = {"step": int(step_name.split('_')[-1])}

            # Add folder and other run dataframe information
            for key, val in run_df.items(): 
                if key in run_include:
                    step_d[key]=run_df[key][run_index]

            # Get properties of interest from parameter file
            editor.read_par()
            editor.reverse_search=False
            editor.max_search_hits=1
            step_d["phase_fraction"],step_d["phase_fraction_e"] = get_value(key="_pd_phase_atom_%", editor=editor)
            step_d["n_phases"] = len(step_d["phase_fraction"])
            step_d["Rwp"],_ = get_value(key="_refine_ls_wR_factor_all", editor=editor)
            step_d["Rexp"],_ = get_value(key="_refine_ls_goodness_of_fit_all", editor=editor)
            step_d["Rwp"]=step_d["Rwp"][0]
            step_d["Rexp"]=step_d["Rexp"][0]
            if step_d["Rexp"]<=0.0:
                step_d["GOF"] = NAN
            else:
                step_d["GOF"] = step_d["Rwp"] / step_d["Rexp"]

            # Phase parameters 
            editor.reverse_search=True
            editor.max_search_hits=step_d["n_phases"]
            editor.get_phases(use_stored_par=True)         
            step_d["phase_name"] = editor.value
            step_d["lattice_a"],step_d["lattice_a_e"] = get_value(key="_cell_length_a", editor=editor)
            step_d["lattice_b"],step_d["lattice_b_e"] = get_value(key="_cell_length_b", editor=editor)
            step_d["lattice_c"],step_d["lattice_c_e"] = get_value(key="_cell_length_c", editor=editor)
            step_d["lattice_alpha"],step_d["lattice_alpha_e"] = get_value(key="_cell_angle_alpha", editor=editor)
            step_d["lattice_beta"],step_d["lattice_beta_e"] = get_value(key="_cell_angle_beta", editor=editor)
            step_d["lattice_gamma"],step_d["lattice_gamma_e"] = get_value(key="_cell_angle_gamma", editor=editor)
            step_d["biso"],step_d["biso_e"] = get_value(key="_atom_site_B_iso_or_equiv", editor=editor)
            step_d["crystallite_size"],step_d["crystallite_size_e"] = get_value(key="_riet_par_cryst_size", editor=editor)
            step_d["microstrain"],step_d["microstrain_e"] = get_value(key="_riet_par_rs_microstrain", editor=editor)

            # Put png files in step dictionary
            for png_index, png_file in enumerate(sorted(png_files)):
                title=str(png_file.stem).split("plot_")[-1]
                title = title.replace(" ","_")
                title = title.replace(".","p")
                step_d[f'FILE{png_index}_{title}'] = str(png_file)

            # Tidy the dictionary and append to cinema dataframe
            step_d = tidy_dictionary(step_d,step_d["n_phases"])
            for d in step_d:
                cinema_d.append(d)
   
    cinema_df = pd.DataFrame.from_dict(cinema_d)             
    cinema_df.to_csv('data.csv', index=False, na_rep='NaN')
    Path('test.pong').parts
if __name__ == '__main__':
    main()
    MILK.cinema.main()

    