import argparse
import MILK
from pathlib import Path
import numpy as np
import json


def get_arguments():
    # Parse user arguments
    welcome = "Commandline maud esg loader for 2D x-ray diffraction."
    parser = argparse.ArgumentParser(description=welcome)

    parser.add_argument("FILE", type=str,
                        help="Input MAUD parameter file containing 'Inclined Reflection Image' detector objects")
    parser.add_argument("-d", "--detectors", nargs="+", required=True,
                        help="Detector names in MAUD parameter file. len(maud_detectors)=len(esg_files)")
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Directory where to store the output data. Default is data directory of first file.")
    parser.add_argument("--pixel1", type=float, default=200*1e-6,
                        help="pixel size along y in meters.")
    parser.add_argument("--pixel2", type=float, default=200*1e-6,
                        help="pixel size along x in meters.")
    parser.add_argument("--max_shape", nargs=2, type=float, default=[2048, 2048],
                        help="pixel size along x.")
    opts = parser.parse_args()

    # opts.FILE = "Calibrated_geometry.par"
    # opts.detectors = ["det1","det2","det3","det4"]

    opts.detector_config = {"pixel1": opts.pixel1,
                            "pixel2": opts.pixel2, "max_shape": opts.max_shape}
    if opts.output is not None:
        opts.output = Path(opts.output)

    return opts


def write_poni(wavelength, distance, x, y, rot1, rot2, rot3, detector_config, detector, file):
    with open(file, 'w') as f:
        f.write(f"# PONI exported from MAUD {detector} detector\n")
        f.write("poni_version: 2\n")
        f.write(f"Detector: Detector\n")
        f.write(f"Detector_config: {json.dumps(detector_config)}\n")
        f.write(f"Distance: {distance}\n")
        f.write(f"Poni1: {y}\n")
        f.write(f"Poni2: {x}\n")
        f.write(f"Rot1: {rot1}\n")
        f.write(f"Rot2: {rot2}\n")
        f.write(f"Rot3: {rot3}\n")
        f.write(f"Wavelength: {wavelength}\n")


def entry_point():
    args = get_arguments()
    main(args.FILE, args.detectors, args.detector_config, args.output)

def main(file: str, detectors: list, detector_config: dict, output: Path() = None):
    """Exports poni detector file from MAUD inclined detector geometry.

    Args:
        file (str): _description_
        detectors (list(str)): _description_
        detector_config (dict): contains a dict of detector parameters for integration e.g. {"pixel1": opts.pixel1,
                            "pixel2": opts.pixel2, "max_shape": opts.max_shape}
        output (Path(), optional): Path to output directory . Defaults to None.
    """
    # Configure output
    if output is None:
        output = Path(file).parent
    output.mkdir(exist_ok=True)

    # Load parameter file and export poni's
    editor = MILK.parameterEditor.editor()
    editor.ifile = file
    editor.run_dirs = ""
    editor.wild = [0]
    editor.wild_range = [[]]
    editor.read_par()
    for detector in detectors:

        editor.get_val(key='_inst_angular_calibration',
                       sobj=detector, use_stored_par=True)
        if "'Inclined" in editor.value:
            editor.get_val(key='_diffrn_radiation_wavelength&',
                           sobj=detector, use_stored_par=True)
            wavelength = float(editor.value[0])/1e10
            editor.get_val(key='_pd_instr_dist_spec/detc',
                           sobj=detector, use_stored_par=True)
            distance = float(editor.value[0])/1e3
            editor.get_val(key='_image_original_center_x',
                           sobj=detector, use_stored_par=True)
            xo = float(editor.value[0])/1e3
            editor.get_val(key='_image_original_center_y',
                           sobj=detector, use_stored_par=True)
            yo = float(editor.value[0])/1e3
            editor.get_val(key='_inst_ang_calibration_center_x',
                           sobj=detector, use_stored_par=True)
            dx = float(editor.value[0])/1e3
            editor.get_val(key='_inst_ang_calibration_center_y',
                           sobj=detector, use_stored_par=True)
            dy = float(editor.value[0])/1e3
            x = xo+dx
            y = yo+dy

            # Get angles
            editor.get_val(key='_inst_ang_calibration_detc_2theta',
                           sobj=detector, use_stored_par=True)
            rot2 = np.deg2rad(-float(editor.value[0]))
            editor.get_val(key='_inst_ang_calibration_detc_phiDA',
                           sobj=detector, use_stored_par=True)
            rot1 = np.deg2rad(float(editor.value[0]))
            editor.get_val(key='_inst_ang_calibration_detc_etaDA',
                           sobj=detector, use_stored_par=True)
            rot3 = np.deg2rad(float(editor.value[0]))
            editor.get_val(key='_inst_ang_calibration_detc_omegaDN',
                           sobj=detector, use_stored_par=True)
            omega = np.deg2rad(float(editor.value[0]))
            assert omega == 0, "Cannot have non-zero omega and have PONI compliant detector!"
            # Export poni
            write_poni(wavelength, distance, x, y, rot1, rot2, rot3,
                       detector_config, detector, output / f"{detector}_maud.poni")
        else:
            print(
                f"detector {detector} was not found or did not have an 'Inclined Reflection Image' angular calibration.")


if __name__ == "__main__":
    args = get_arguments()
    main(args.FILE, args.detectors, args.detector_config, args.output)
