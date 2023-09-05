import MILK
from pathlib import Path
import numpy as np
import os
import shutil

class Poni(object):
    """ Class that stores calibration settings for a single detector.
    """

    def __init__(self, poni_file):
        self.load_poni(poni_file)

    def load_poni(self, file):
        with open(file) as fp:
            poni_lines = fp.readlines()
        poni_lines = poni_lines[-9:]
        for line in poni_lines:
            try:
                name, value = line.split(":")
            except ValueError:
                continue
            if name == "PixelSize1":
                self.pixel1 = float(value)
            elif name == "PixelSize2":
                self.pixel2 = float(value)
            elif name == "Distance":
                self.distance = float(value)
            elif name == "Poni1":
                self.poni1 = float(value)
            elif name == "Poni2":
                self.poni2 = float(value)
            elif name == "Rot1":
                self.rot1 = float(value)
            elif name == "Rot2":
                self.rot2 = float(value)
            elif name == "Rot3":
                self.rot3 = float(value)
            elif name == "Wavelength":
                self.wavelength = float(value)

    def update_poni_in_par(self, detector, maud_par):

        editor = MILK.parameterEditor.editor()
        editor.ifile = maud_par
        editor.ofile = maud_par
        editor.run_dirs = ""
        editor.wild = [0]
        editor.wild_range = [[]]
        editor.read_par()
        editor.get_val(key="_inst_angular_calibration",
                       sobj=f"{detector} Inclined&Reflection&Image", use_stored_par=True)
        if editor.value == []:
            print(
                f"The detector named {detector} is not an inclined reflection image detector. PONI could not be set.")
            return
        editor.set_val(key="_image_original_dist_spec/detc",
                       value=f"{self.distance*1000.0}", sobj=f"{detector} Inclined&Reflection&Image", use_stored_par=True)
        editor.set_val(key="_image_original_center_x",
                       value=f"{self.poni2*1000.0}", sobj=f"{detector} Inclined&Reflection&Image", use_stored_par=True)
        editor.set_val(key="_image_original_center_y",
                       value=f"{self.poni1*1000.0}", sobj=f"{detector} Inclined&Reflection&Image", use_stored_par=True)
        editor.set_val(key="_image_original_detc_2theta",
                       value=f"{np.rad2deg(-self.rot2)}", sobj=f"{detector} Inclined&Reflection&Image", use_stored_par=True)
        editor.set_val(key="_image_original_detc_phiDA",
                       value=f"{np.rad2deg(self.rot1)}", sobj=f"{detector} Inclined&Reflection&Image", use_stored_par=True)
        editor.set_val(key="_image_original_detc_omegaDN",
                       value=f"{0.0}", sobj=f"{detector} Inclined&Reflection&Image", use_stored_par=True)
        editor.set_val(key="_image_original_detc_etaDA",
                       value=f"{np.rad2deg(self.rot3)}", sobj=f"{detector} Inclined&Reflection&Image", use_stored_par=True)

        editor.set_val(key="_pd_instr_dist_spec/detc",
                       value=f"{self.distance*1000.0}", sobj=f"{detector} Inclined&Reflection&Image", use_stored_par=True)
        editor.set_val(key="_inst_ang_calibration_center_x",
                       value=f"{0.0}", sobj=f"{detector} Inclined&Reflection&Image", use_stored_par=True)
        editor.set_val(key="_inst_ang_calibration_center_y",
                       value=f"{0.0}", sobj=f"{detector} Inclined&Reflection&Image", use_stored_par=True)
        editor.set_val(key="_inst_ang_calibration_detc_2theta",
                       value=f"{np.rad2deg(-self.rot2)}", sobj=f"{detector} Inclined&Reflection&Image", use_stored_par=True)
        editor.set_val(key="_inst_ang_calibration_detc_phiDA",
                       value=f"{np.rad2deg(self.rot1)}", sobj=f"{detector} Inclined&Reflection&Image", use_stored_par=True)
        editor.set_val(key="_inst_ang_calibration_detc_omegaDN",
                       value=f"{0.0}", sobj=f"{detector} Inclined&Reflection&Image", use_stored_par=True)
        editor.set_val(key="_inst_ang_calibration_detc_etaDA",
                       value=f"{np.rad2deg(self.rot3)}", sobj=f"{detector} Inclined&Reflection&Image", use_stored_par=True)
        editor.set_val(key="_diffrn_radiation_wavelength",
                       value=f"{self.wavelength*1e10}", sobj=detector, use_stored_par=True)
        editor.set_val(key="_diffrn_radiation_wavelength_wt",
                       value="1.0", sobj=detector, use_stored_par=True)
        
        #Also reset the angle range so full range of PONI is displayed
        editor.set_val(key="_pd_proc_2theta_range_min",
                       value="0.0", sobj=detector, use_stored_par=True)
        editor.set_val(key="_pd_proc_2theta_range_max",
                       value="0.0", sobj=detector, use_stored_par=True)
        editor.write_par()


def build_omega(n_files, omega_start, omega_step):
    return [omega_start+n*omega_step for n in range(0, n_files)]


def update_angle_in_esg(esg_file, omega, key="_pd_meas_angle_omega"):
    """
    Update the esg file inplace to contain the omega measurement angle.
    Note it is assumed the first angle reference is the only reference! Done avoid reading large files
    Can also use _pd_meas_angle_omega, _pd_meas_angle_chi,_pd_meas_angle_phi
    """
 
    keyval = bytes(f"{key} {float(omega):.6}\n", 'utf-8')
    with open(esg_file, 'rb+') as f1:
        for line in f1:
            if b'{key}' in line:
                f1.seek(idx)
                f1.write(keyval)
                break
            idx = f1.tell()


def update_script(script, command):
    script.append(command)
    return script


def write_script(script, filename):
    with open(filename, 'w') as f:
        for line in script:
            f.write(f"{line}\n")


def write_maud_batch_script(maud_batch_script, maud_output_par, maud_load_script, cwd):
    script = ["_maud_working_directory",
              f"'{cwd.absolute()}{os.sep}'",
              "",
              "loop_",
              "_riet_analysis_file",
              "_riet_analysis_iteration_number",
              "_maud_remove_all_datafiles",
              "_riet_meas_datains_name",
              "",
              f"'{Path(maud_output_par)}' 0 'true' '{maud_load_script}'"]
    write_script(script, cwd / maud_batch_script)


def main(esg_files: list[str],
         maud_detectors: list[str],
         maud_input_par: str,
         maud_output_par: str = None,
         poni_files: list[str]=None,
         omega: list[float] = None,
         chi:list[float] = None,
         phi:list[float] = None,
         output: Path = Path().cwd(),
         maud_batch_script: str = "batch.ins",
         maud_load_script: str = "load_data.ins",
         maud_run_import: bool = True):
    """Copy esg files into MAUD detector objects in input par file. 

    Args:
        -esg_files (list[str]): esg_files of len detector

        -maud_detectors (list[str]): MAUD input par file detector list corresponding to esg_files.

        -maud_input_par (str): Absolute path to template MAUD parameter file containing appropriate detector objects.

        -maud_output_par (str, optional): Output name for MAUD parameter file. Defaults to maud_input_par.

        -poni_files (list[str]): pyFAI PONI for inclined detector geometry in MAUD. If specified, the script will update  MAUD detector parameters with those from the PONI. Defaults to None.
        
        -omega (list[float], optional): Omega measurement angle of len esg_files. Defaults to None.
        
        -chi (list[float], optional): Chi measurement angle of len esg_files. Defaults to None.
        
        -phi (list[float], optional): Phi measurement angle of len esg_files. Defaults to None.
        
        -output (Path, optional): output directory for outputs. Defaults to Path().cwd().
        
        -maud_batch_script (str, optional): MAUD batch interface script. Defaults to "batch.ins".
        
        -maud_load_script (str, optional): MAUD generated detector/esg pairs. Defaults to "load_data.ins".
        
        -maud_run_import (bool, optional): Call MAUDText and do import. Defaults to True.
    """

    # Configure the output directory
    output.mkdir(exist_ok=True)

    # Build data load script and write
    data_load_script = ["loop_", "_pd_meas_dataset_id",
                        "_riet_meas_datafile_name", ""]
    for esg_file, maud_detector in zip(esg_files, maud_detectors):
        data_load_script = update_script(
            data_load_script, f"'{maud_detector}' '.{os.sep}{os.path.relpath(esg_file,output)}'")


    write_script(data_load_script, output / maud_load_script)

    # Write batch script
    if maud_output_par is None:
        maud_output_par = maud_input_par.name
    else:
        maud_output_par = Path(maud_output_par).name

    write_maud_batch_script(maud_batch_script,
                            maud_output_par, maud_load_script, output)

    # Update measurement angles for esg files
    if omega is not None:
        for omega, esg_file in zip(omega, esg_files):
            update_angle_in_esg(esg_file, omega,key="_pd_meas_angle_omega")
    if chi is not None:
        for chi, esg_file in zip(chi, esg_files):
            update_angle_in_esg(esg_file, chi,key="_pd_meas_angle_chi")
    if phi is not None:
        for phi, esg_file in zip(phi, esg_files):
            update_angle_in_esg(esg_file, phi,key="_pd_meas_angle_phi")
        
    # Copy input MAUD file to output file
    shutil.copyfile(maud_input_par, output / maud_output_par)

    # Update MAUD file with poni
    for poni_file, maud_detector in zip(poni_files, maud_detectors):
        if poni_file is not None:
            poni = Poni(poni_file)
            poni.update_poni_in_par(
                maud_detector, str(output / maud_output_par))
    

    # Run import using MILK
    if maud_run_import:
        MILK.MAUDText.callMaudText.run_MAUD(
            os.getenv('MAUD_PATH').strip("'"),
            "mx8G",
            'False',
            None,
            str(output / maud_batch_script)
        )
