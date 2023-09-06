import pickle
from functools import partial
from pathos.pools import ProcessPool as pPool
import fabio
import numpy as np
from pathlib import Path
from pyFAI import multi_geometry
# from pyFAI import ext
import tqdm
import os
# from scipy import stats
import json
from pyFAI.io import DefaultAiWriter
from matplotlib.pyplot import subplots, close
from pyFAI.gui import jupyter
import matplotlib
from pyFAI.ext.invert_geometry import InvertGeometry
from pyFAI.gui.utils.unitutils import from2ThRad,tthToRad
from pyFAI import units
matplotlib.use('Agg')
import copy

def write_json():
    """Write a template json file for integration."""
    with open('template.azimint.json', 'w') as f:
        json_object = json.dump({
            "poni_file": [""],
            "do_mask": True,
            "mask_file": [""],
            "do_dark": False,
            "dark_file": [""],
            "dark_norm": 1.0,
            "do_bright": False,
            "bright_file": [""],
            "bright_norm": 1.0,
            "data_ops": [""],
            "do_polarization": False,
            "polarization_factor": 0.99,
            "do_2D": False,
            "unit": "2th_deg",
            "npt_radial": 2000,
            "do_radial_range": True,
            "radial_range": [8, 70],
            "npt_azimuth": 72,
            "do_azimuthal_range": False,
            "azimuth_range": [0, 360],
            "chi_discontinuity_at_0": True,
            "do_solid_angle": True,
            "do_remove_nan": True,
            "error_model": "Poisson",
            "method": [
                "full",
                "histogram",
                "cython"
            ],
            "opencl_device": "cpu"
        }, f)


class Diffraction(object):
    """ Class that stores calibration settings for a single detector
    and the raw data.
    """

    def __init__(self, poni, data_ops, mask_file,
                 bright_file=None, bright_norm=None, dark_file=None, dark_norm=None):

        # store input files
        self.poni = poni
        self.data_ops = data_ops
        self.mask_file = mask_file
        self.bright_file = bright_file
        self.bright_norm = bright_norm
        self.dark_file = dark_file
        self.dark_norm = dark_norm
        self.darkbright = None

        # read some more information about calibration
        with open(self.poni) as fp:
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

        # load, normalize, and add dark and bright
        if bright_file is not None:
            self.bright = self.load_and_process(bright_file, bright_norm)
            self.darkbright = self.bright
        else:
            self.bright = None

        if dark_file is not None:
            self.dark = self.load_and_process(dark_file, dark_norm)
            if self.darkbright is None:
                self.darkbright = self.dark
            else:
                self.darkbright += self.dark
        else:
            self.dark = None

        if mask_file is not None:
            self.mask = self.apply_ops(fabio.open(mask_file).data)
        else:
            self.mask = None

    def load_and_process(self, file, norm):
        data = self.apply_ops(fabio.open(file).data)
        data = self.normalize(data, norm)
        return data

    # TODO remove
    # def tif_loader_generic(self, files, data_type="int32"):
    #     # load operation
    #     data = []
    #     for file in files:
    #         fimage = PIL.Image.open(file)
    #         data.append(np.asarray(fimage, data_type))
    #     return data

    def normalize(self, data, norm):
        for i, d in enumerate(data):
            data[i] = d / norm
        return data

    def apply_ops(self, data: np.array):
        for op in self.data_ops:
            #print("Doing operation {}".format(op))
            # flip vertical operation
            if op == "flipud":
                data = np.flipud(data)
            # flip horizontal operation
            elif op == "fliplr":
                data = np.fliplr(data)
            # rotate clockwise operation
            elif op == "rotcw":
                data = np.rot90(data, 3)
            # rotate counter-clockwise operation
            elif op == "rotccw":
                data = np.rot90(data)
            elif op == "":
                pass
            else:
                raise NotImplementedError("Do not understand data operation "
                                          "{}".format(op))
        return data


def cake2MAUD(ai, unit, result, sigmas, data, mask, id):
    """cake2MAUD converts histograms (e.g. 2theta vs intensity) to detector position vs intensity.

    Args:
        ai (object): Integrator object.
        result (object): pyFAI result integration objection
        sigmas (np.array): Uncertainty in intensity.
        data (np.array): Tiff data.
        mask (np.array): Tiff mask.
        id (int): Detector index.

    Returns:
        Intensity (np.array):  Intensity.
        X (np.array): X position on detector.
        Y (np.array): Y position on detector.
        Sigmas (np.array): Uncertainty in intensity.
    """

    def export_interpolation(result,ai,unit,fname):
        """Interpolate detector position and angles."""
        print("Regenerating can take some time (usually 2-6 minutes per detector instance depending on detector size).")
        # Convert a generic radial unit to radial meters
        directDist=ai.getFit2D()["directDist"]
        tthrad = tthToRad(result.radial,unit=unit, wavelength=ai.wavelength, directDist=directDist)
        radial = from2ThRad(tthrad,unit=units.R_M,directDist=directDist,ai=ai)
        
        # Get azimuthal angle and meshgrid with radial
        chi = np.deg2rad(result.azimuthal)
        radial_bin,chi_bin = np.meshgrid(radial,chi)

        # Invert geometry and perform interpolation such that 
        # X_bin and Y_bin hold the detector coordinates of some 
        # 2theta,chi bin
        r=ai.rArray()
        c=ai.chiArray()
        ig = InvertGeometry(r,c)
        t = ig.many(radial_bin,chi_bin,refined=True)
        X_bin = 1e3*(t[:,:,1]*ai.pixel2-ai.poni2+ai.pixel2/2.0)
        Y_bin = 1e3*(t[:,:,0]*ai.pixel1-ai.poni1+ai.pixel1/2.0)

        # Store so only a one time cost
        with open(fname, 'wb') as f:
            pickle.dump(result.radial, f)
            pickle.dump(result.azimuthal, f)
            pickle.dump(X_bin, f)
            pickle.dump(Y_bin, f)

        return X_bin, Y_bin

    def load_interpolation(fname):
        with open(fname, 'rb') as f:
            radial_stored = pickle.load(f)
            azimuthal_stored = pickle.load(f)
            X_bin = pickle.load(f)
            Y_bin = pickle.load(f)
        return X_bin, Y_bin, radial_stored, azimuthal_stored

    def get_bin_detector_location(result, ai, unit, fname):
        """Compare key metrics to see if interpolation is good."""
        if Path(fname).is_file():
            X_bin, Y_bin, radial_stored, azimuthal_stored = load_interpolation(
                fname)
            if all(radial_stored == result.radial) and all(azimuthal_stored == result.azimuthal):
                return X_bin, Y_bin
            return export_interpolation(result, ai, unit, fname)
        else:
            return export_interpolation(result, ai, unit, fname)

    # Using a cache for the detector, extract bin locations
    X_bin,Y_bin = get_bin_detector_location(result, ai, unit, fname = f"binned_detector_coord{id}")

    # Create a bin level mask
    imask = np.ma.masked_invalid(X_bin).mask | np.ma.masked_invalid(
        Y_bin).mask | np.ma.masked_invalid(result.intensity).mask #| (result.intensity == 0)
    X_bin = np.ma.masked_array(X_bin, imask)
    Y_bin = np.ma.masked_array(Y_bin, imask)
    intensity = np.ma.masked_array(result.intensity, imask)
    sigmas = np.ma.masked_array(sigmas, imask)

    return intensity, X_bin, Y_bin, sigmas


def write_esg_detector(i_2dm, x_2dm, y_2dm, weight_2dm, chi_2d, fname, distance):
    """Write  data formatted for inclined detector geometry in MAUD.

    Args:
        i_2dm (np.array): Intensity for each histogram
        x_2dm (np.array): X position for each histogram
        y_2dm (np.array): Y position for each histogram.
        weight_2dm (np.array): Uncertainty in intensityfor each histogram.
        chi_2d (np.array): Chi position for each histogram in i_2dm, x_2dm, etc.
        fname (str): Output file name.
        distance (float): detector distance.
    """
    blockid = 0

    f = open(fname, "w")
    f.write("_pd_block_id noTitle|#%d\n" % (blockid))
    f.write("\n")
    f.write("_diffrn_detector 2D\n")
    f.write("_diffrn_detector_type CCD like\n")
    f.write("_pd_meas_step_count_time ?\n")
    f.write("_diffrn_measurement_method diffraction_image\n")
    f.write("_diffrn_measurement_distance_unit mm\n")
    f.write("_pd_instr_dist_spec/detc %f\n" % (distance))
    f.write("_diffrn_radiation_wavelength ?\n")
    f.write("_diffrn_source_target ?\n")
    f.write("_diffrn_source_power ?\n")
    f.write("_diffrn_source_current ?\n")
    f.write("_pd_meas_angle_omega 0.0\n")
    f.write("_pd_meas_angle_chi 0.0\n")
    f.write("_pd_meas_angle_phi 0.0\n")
    f.write("_pd_meas_orientation_2theta 0\n")
    f.write("_riet_par_spec_displac_x 0\n")
    f.write("_riet_par_spec_displac_y 0\n")
    f.write("_riet_par_spec_displac_z 0\n")
    f.write("_riet_meas_datafile_calibrated false\n")
    index = np.argsort(chi_2d)
    chi_2d[chi_2d < 0] += 360
    for i in index:
        intensities = i_2dm[i].compressed()
        if len(intensities) > 0:
            xs = x_2dm[i].compressed()
            ys = y_2dm[i].compressed()
            weights = weight_2dm[i].compressed()
            f.write("_pd_block_id noTitle|#%d\n" % (blockid))
            f.write("\n")
            f.write("_pd_meas_angle_eta %f\n" % (chi_2d[i]))
            f.write("\n")
            f.write("loop_\n")

            f.write(
                "_pd_meas_position_x _pd_meas_position_y _pd_meas_intensity_total _pd_meas_intensity_sigma\n")
            for x, y, intensity, weight in zip(xs, ys, intensities, weights):
                f.write("%f %f %f %f\n" % (x, y, intensity, weight))
            f.write("\n")
            blockid += 1
    f.close()


def write_esg1(radial, intensities, azimuthal, sigmas, file):
    """Write MAUD esg formatted histogram data to single file."""
    Path(file).unlink(missing_ok=True)
    with open(file, 'a+') as f:
        for i, (intensity, azimuth, sigma) in enumerate(zip(intensities, azimuthal, sigmas)):
            imask = np.ma.masked_invalid(intensity).mask
            intensity_masked = np.ma.masked_array(
                intensity, imask).compressed()
            if len(intensity_masked) > 0:
                radial_masked = np.ma.masked_array(radial, imask).compressed()
                sigma_masked = np.ma.masked_array(sigma, imask).compressed()
                header = f"\n_pd_block_id noTitle|#{i}\n" \
                    f"_pd_meas_angle_eta {azimuth}\n" \
                    f"_pd_meas_angle_omega {0.0}\n\n" \
                    f"loop_\n" \
                    f"_pd_meas_position_x _pd_meas_intensity_total _pd_proc_intensity_weight"
                np.savetxt(f,
                           np.c_[radial_masked, intensity_masked, sigma_masked],
                           delimiter='\t',
                           header=header,
                           comments='')


def write_spectra(mg, radial, intensity, sigma, stem, fmt, chi, opts):
    """Write spectra to different Rietveld/Cinema compatible formats."""
    file = f"{stem}.{fmt}"
    Path(file).unlink(missing_ok=True)
    header = [f"{file}"]

    if opts["do_remove_nan"]:
        exclude = np.isnan(intensity)
        if np.all(exclude):
            return
        else:
            radial = radial[~exclude]
            intensity = intensity[~exclude]
            sigma = sigma[~exclude]

    if fmt == 'dat':
        daw = DefaultAiWriter(filename=file, engine=mg)
        daw.save1D(filename=file,
                   dim1=radial,
                   I=intensity,
                   error=sigma,
                   dim1_unit=opts["unit"],
                   has_dark=opts["do_dark"],
                   polarization_factor=opts["polarization_factor"] if opts["do_polarization"] else None,
                   has_mask=opts["do_mask"])
        daw.close()
    elif fmt == 'fxye':
        assert opts["unit"] in "2th_deg", "Can only do fxye with 2th_deg unit. TODO add conversions"
        header.append(
            f"BANK 1 {len(radial)} {len(radial)} CONS {radial[0]} {radial[1]-radial[0]} 0 0 FXYE")
        np.savetxt(file,
                   np.c_[100*radial, intensity, sigma],
                   delimiter='\t',
                   header='\n'.join(header),
                   comments='')
    elif fmt == 'xye':
        header = [f"# {h}" for h in header]
        header.insert(0, "/*")
        header.append("*/")
        np.savetxt(file,
                   np.c_[radial, intensity, sigma],
                   delimiter='\t',
                   header='\n'.join(header),
                   comments='')
    elif "xy" in fmt:
        if fmt == "xy-noheader":
            header = []
            file = file.replace(".xy-noheader", "noheader.xy")
        else:
            header = [f"# {h}" for h in header]
            header.insert(0, "/*")
            header.append("*/")
            header = '\n'.join(header)
        np.savetxt(file,
                   np.c_[radial, intensity],
                   delimiter='\t',
                   header=header,
                   comments='')
    elif fmt == "esg":
        header = f"_pd_block_id noTitle|#0\n" \
            f"_pd_meas_angle_eta {chi}\n" \
            f"_pd_meas_angle_omega {0.0}\n" \
            f"loop_\n" \
            f"_pd_meas_position_x _pd_meas_intensity_total _pd_proc_intensity_weight"
        write_esg1(radial, [intensity], [chi], [sigma], file)

    elif fmt == "esg2":
        return
    else:
        print("fmt is not yet implemented")
        raise NotImplementedError


def initialize_detectors(opts):
    """Create a list of diffraction objects which handle detector initialization.

    Args:
        opts (dict): Options pass at program call

    Returns:
        list(Diffraction): List of initialized diffraction instances.
    """
    # load data and poni files
    detectors = []
    for poni_file, data_ops, mask, bright_file, dark_file in zip(opts["poni_file"],
                                                                 opts["data_ops"],
                                                                 opts["mask_file"],
                                                                 opts["bright_file"],
                                                                 opts["dark_file"]
                                                                 ):
        detectors.append(Diffraction(poni_file,
                                     data_ops.split(' '),
                                     mask if opts["do_mask"] else None,
                                     bright_file if opts["do_bright"] else None,
                                     opts["bright_norm"],
                                     dark_file if opts["do_dark"] else None,
                                     opts["dark_norm"]
                                     ))
    return detectors


def initialize_integrator(detectors, opts):
    """Configure integrator."""
    # load calibration
    return multi_geometry.MultiGeometry(
        [detector.poni for detector in detectors],
        unit=opts["unit"],
        radial_range=opts["radial_range"] if opts["do_radial_range"] else [None,None],
        azimuth_range=opts["azimuth_range"] if opts["do_azimuthal_range"] else [
            0, 360],
        empty=np.nan,
        chi_disc=0)
#

def integrate(detectors, output, overwrite, formats, histogram_plot, opts, prefix, images):
    """Wrapper function to 1d and 2d integrations which imports the data and calls integration schemes."""
    if prefix is None:
        stem = output / f"{Path(images[0]).stem}"
    else:
        stem = output / prefix

    if not overwrite and list(Path().rglob(f"{stem}*")) != []:
        # Nothing to do
        return

    # Get data
    data = []
    for image, detector in zip(images, detectors):
        if detector.darkbright is None:
            data.append(detector.load_and_process(
                image, 1.0))
        else:
            data.append(detector.load_and_process(
                image, 1.0)-detector.darkbright)

    # Get mask
    mask = [detector.mask for detector in detectors]

    # Update mask from data
    # for i, _ in enumerate(data):
    #     mask[i][data[i] <= 0] = True

    # Construct integrators
    mg = initialize_integrator(detectors, opts)

    # Execute using the best available integrator
    if opts["npt_azimuth"] == 1 and not opts["do_2D"]:
        integration1d(mask, mg, data, opts, stem, formats, histogram_plot)
    else:
        integration2d(mask, mg, data, opts, stem, formats, histogram_plot)


def integration1d(mask, mg, data, opts, stem, formats, histogram_plot):
    """Perform full integration of multigeometry diffraction image.

    Args:
        mask (numpy array): 2D numpy array of shape(data) describing pixels to excluding during integration.
        mg (list pyfai integrators): List of pyfai integrators describing the geometry, dark files, integration ranges, etc.
        data (numpy array): 2D numpy array of an diffraction image.
        opts (dict): Dictionary of azimint.json init file.
        stem (str): Stem of image for integrated file naming.
    """
    result = mg.integrate1d(lst_data=data,
                            npt=opts["npt_radial"],
                            lst_mask=mask,
                            polarization_factor=opts["polarization_factor"] if opts["do_polarization"] else 0,
                            method=opts["method"],
                            error_model=opts["error_model"],
                            correctSolidAngle=opts["do_solid_angle"])
    
    # Export histogram plot
    if histogram_plot:
        fig, ax = subplots()
        jupyter.plot1d(result, ax=ax)
        fig.savefig(f"{stem}_1dplot.png")
        close(fig)

    if not hasattr(result, "sigma") or result.sigma is None:
        result.intensity[result.intensity < 0] = np.nan
        sigma = np.ones(np.shape(result.intensity))/np.sqrt(result.intensity)
    else:
        sigma = result.sigma

    # Generic export format
    for format in formats:
        write_spectra(mg, result.radial, result.intensity,
                      sigma, stem, format, 0.0, opts)


def integration2d(mask, mg, data, opts, stem, formats, histogram_plot):
    """Perform caked integration of multigeometry diffraction image.

    Args:
        mask (numpy array): 2D numpy array of shape(data) describing pixels to excluding during integration.
        mg (list pyfai integrator): List of pyfai integrators describing the geometry, dark files, integration ranges, etc.
        data (numpy array): 2D numpy array of an diffraction image.
        opts (dict): Dictionary of azimint.json init file.
        stem (str): Stem of image for integrated file naming.
    """
    result = mg.integrate2d(lst_data=data,
                            npt_rad=opts["npt_radial"],
                            npt_azim=opts["npt_azimuth"],
                            lst_mask=mask,
                            polarization_factor=opts["polarization_factor"] if opts["do_polarization"] else 0,
                            method=opts["method"],
                            error_model=opts["error_model"],
                            correctSolidAngle=opts["do_solid_angle"])
    # Export histogram plot
    if histogram_plot:
        fig, ax = subplots()
        jupyter.plot2d(result, ax=ax)
        fig.savefig(f"{stem}_2dplot.png")
        close(fig)

    if not hasattr(result, "sigma") or result.sigma is None:
        result.intensity[result.intensity < 0] = np.nan
        sigmas = np.ones(np.shape(result.intensity))/np.sqrt(result.intensity)
    else:
        sigmas = result.sigma


    formats = copy.deepcopy(formats)
    # Export esg_detector format if in formats
    if "esg_detector" in formats:
        for i, g in enumerate(mg.ais):
            intensity_det, X_bin_det, Y_bin_det, sigmas_det = cake2MAUD(
                g, mg.unit, result, sigmas, data[i], mask[i], i)
            write_esg_detector(intensity_det, Y_bin_det, X_bin_det,
                               sigmas_det, result.azimuthal, f"{stem}_det{i}_2d.esg", g.get_dist()*1e3)
        formats.pop(formats.index("esg_detector"))

    # Export esg1 format if in formats
    if "esg1" in formats:
        write_esg1(result.radial, result.intensity,
                   result.azimuthal, sigmas, f"{stem}_2d.esg")
        formats.pop(formats.index("esg1"))

    # Generic export format
    for intensity, azimuth, sigma in zip(result.intensity, result.azimuthal, sigmas):
        chi = np.round(azimuth, 1)
        stemazim = f"{stem}_azim_{np.round(azimuth,1)}"
        for format in formats:
            write_spectra(mg, result.radial, intensity,
                          sigma, stemazim, format, chi, opts)


def validate_image_pairs(images):
    """Helper function to handle more complex naming conventions."""
    return np.array(images).transpose()
    # index_remove0 = []
    # index_remove1 = []
    # images_out=[]
    # images0 = np.array(images[0])
    # images1 = np.array(images[1])
    # for image0 in images0:
    #     runid=image0.split('-')[-2]
    #     exist = np.array([runid in image for image in images[1]],dtype=bool)
    #     if any(exist):
    #         print([image0,images1[exist]])
    #         images_out.append([str(image0),images1[exist][0]])
    #         # index_remove0.append(i)
    # #     if not any([image1.split('-')[-2] in image for image in images[0]]):
    # #         index_remove1.append(i)
    # # for i in reversed(index_remove0):
    # #     images[0].pop(i)
    # # for i in reversed(index_remove1):
    # #     images[1].pop(i)
    # # for i,(image0,image1) in enumerate(zip(images[0],images[1])):
    # #     print(image0,image1)

    # return images_out


def main(files, json_file, output=None, overwrite=False, poolsize=None, prefix=None, formats=['dat'], histogram_plot=False, quiet=False):
    """Build integration file set, objects, and performed integration in parallel.

    Args:
        -file (list(str)): Input file(s) for integration. parsed using pathlib glob and can contain wild cards.

        -json (str): Configuration file for integration.

        -output (str, optional): Directory for files to be saved to. Defaults to None.

        -overwrite (bool, optional): Overwrite previous integration results. Defaults to False.

        -poolsize (int, optional): Number of processors to use. Defaults to None.

        -prefix (str,optional): A string to be used as the file name. If None, the code uses the file name. Defaults to None.

        -format (list(str), optional): Export format of integration result. options ["dat", "xy", "xye", "xy-noheader", "fxye", "esg", "esg1", "esg_detector"].
        
        -histogram_plot (bool, optional): Export png histogram plots . Defaults to 'False'.
        
        -quiet (bool, optional): Turn off terminal messages. Defaults to 'False'.
    """
    # Load integration options file
    with open(json_file, 'r') as f:
        opts = json.load(f)

    # Build detector objects from poni and opts
    detectors = initialize_detectors(opts)

    # Construct image set of size N_file_in_set x N_sets
    images = []
    for file in files:
        images.append(sorted([str(p) for p in Path().rglob(file)]))
    images = validate_image_pairs(images)

    # Configure the output directory
    if output is None:
        output = Path(files[0]).parent
    output.mkdir(exist_ok=True)

    # Check for esg_detector pickled objects and ensure that the binned detector 
    # coordinates have been generated for the current integration scheme
    if 'esg_detector' in formats:
        if not quiet:
            print("Output format esg_detector selected.")
            print("Ensuring binned detector coordinates have been generated appropriately.")
        integrate(detectors, output, overwrite, formats,
                  histogram_plot, opts, prefix, images[0])

    # Setup the mapper
    if poolsize == 1:
        mapper = map
    else:
        pool = pPool(poolsize)
        mapper = pool.imap

    # Call main function in parallel
    # if quiet:
    #     mapper(partial(integrate, detectors, output,
    #                    overwrite, formats, histogram_plot, opts, prefix), images)
    # else:
    #     print("")
    #     print(f"Using {poolsize} of {os.cpu_count()} cpus.")
    #     [print(f"File inputs are {file}") for file in files]
    #     print(f"Output directory is {output}")
    #     [print(f"Exporting file formats {format}") for format in formats]

    #     list(tqdm.tqdm(mapper(partial(integrate, detectors, output, overwrite, formats, histogram_plot, opts, prefix),
    #                           images), total=len(images)))

    # Use for debugging
    integrate(detectors, output, overwrite, formats,
              histogram_plot, opts, prefix,images[0])

    # Cleanup parallel environment if relevant
    if poolsize != 1:
        pool.close()

