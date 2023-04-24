import argparse
from functools import partial
from multiprocessing import Pool, freeze_support
import fabio
import PIL
import numpy as np
from pathlib import Path
import math
import pyFAI
from pyFAI import multi_geometry
from pyFAI import ext
import tqdm
import os
import ge2tiff
from fabio import GEimage
import time
from datetime import datetime
from copy import deepcopy
from scipy import stats

def get_arguments():
    #Parse user arguments
    welcome = "Commandline integration tool for 2D tifs with averaging."
    
    # parse command line
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument("--data-files", nargs="+", required=False)
    parser.add_argument("--poni-files", nargs="+", required=False)
    parser.add_argument("--norm",  type=float, default=1.0)
    parser.add_argument("--norm-exposure-meta",  type=str2bool, default=True, help="Will also apply the exposure as a norm from metadata if available.")
    parser.add_argument("--dir-range", nargs=2, type=int, default=None)
    parser.add_argument("--wild-range", nargs=2, type=int, default=None)
    parser.add_argument("--dark-files", nargs="+", default=None)
    parser.add_argument("--dark-norm",type=float, default=1.0)
    parser.add_argument("--bright-files", nargs="+",default=None)
    parser.add_argument("--bright-norm",type=float, default=1.0)
    parser.add_argument("--mask-files", nargs="+",default=None)
    parser.add_argument("--data-operations", nargs="+",default=None,
        help="choices are flipud,fliplr,rotcw,rotccw")
    parser.add_argument("--strid", type=int,default=1)
    parser.add_argument("--avg-window", type=int,default=1)
    parser.add_argument("--output-path", type=str, default=Path.cwd())
    parser.add_argument("--output-postfix", type=str, default="")  
    parser.add_argument("--output-formats", nargs="+", default=["xye"],
        help="options are fxye, xye, xy, xy-noheader and multiple options can be specified.")
    parser.add_argument("--units", choices=["2th_deg", "2th_rad", "q_nm^-1","q_A^-1", "r_mm"], default="2th_deg")
    parser.add_argument("--npt-radial", type=int, default=1000)
    parser.add_argument("--npt-azim", type=int, default=1)
    parser.add_argument("--radial-range", nargs=2, type=float, default=None)
    parser.add_argument("--azimuth-range", nargs=2, type=float, default=None)
    parser.add_argument("--overwrite", type=str2bool, default=True)
    parser.add_argument("--force-2dintegrator", type=str2bool, default=False)
    parser.add_argument("--method", type=tuple, default=("bbox", "csr", "cython"))
    parser.add_argument("--error-model", type=str, choices=["azimuthal","Poisson"],default="Poisson")
    parser.add_argument("--polarization-factor", type=float,default=None)
    parser.add_argument("--correctSolidAngle", type=str2bool,default=True)
    parser.add_argument("--rot_offset", type=float,default=0)
    parser.add_argument("--pool-size", type=int, default=math.ceil(os.cpu_count()*0.8))
    parser.add_argument("--detector-name",type=str,choices=["ge","pixirad_1ID","pilatus_1ID","generic"],default="generic")
    parser.add_argument("--remove-empty-bins",type=str2bool,default=True)
    parser.add_argument("--omega-rot",type=float,default=0.0)
    opts = parser.parse_args()

    #testing block 
    # opts.data_files = ["analysis/CeO2_calibration/tifs_raw/CeO2_5s_120x120_att000_3000mm_95keV_000017.edf_sum_norm_0_ge1.tif"]
    # opts.poni_files = ["calibrations/ge1.poni"]
    # opts.mask_files = ["calibrations/mask1.edf"]
    # opts.bright_files = None
    # opts.dark_files = None #["BJCL/Dark0pt3_15551*.ge1", "BJCL/Dark0pt3_15551*.ge2", "BJCL/Dark0pt3_15551*.ge3", "BJCL/Dark0pt3_15551*.ge4"]
    # opts.output_formats = ["esg"]
    # opts.output_path = "./"
    # opts.npt_radial = 2500
    # opts.npt_azim=36
    # opts.azimuth_range = [-180,180]#[np.degrees(-0.380),np.degrees(0.045)]
    # opts.radial_range = [2,12]#[0.0003,0.0105]
    # opts.dir_range = [0,20]
    # opts.strid=1
    # opts.avg_window=1
    # opts.norm_exposure_meta=False
    # opts.norm=1
    # opts.dark_norm=1
    # opts.bright_norm=1
    # opts.force_2dintegrator=True
    # # opts.rot_offset=-7.5
    # opts.detector_name="generic"
    # opts.overwrite = True
    # opts.method = ("bbox", "histogram", "cython")

    nponi = len(opts.poni_files)
    if opts.data_operations is None:
        opts.data_operations = [""]*nponi
        
    if opts.mask_files is None:
        opts.mask_files = [None]*nponi

    if opts.bright_files is None:
        opts.bright_files = [None]*nponi

    if opts.dark_files is None:
        opts.dark_files = [None]*nponi


    assert len(opts.data_operations)==nponi, "Length of data_opperations must be same as number of poni_files"
    assert len(opts.mask_files)==nponi, "Length of mask_files must be same as number of poni_files"
    assert len(opts.bright_files)==nponi, "Length of bright_files must be same as number of poni_files"
    assert len(opts.dark_files)==nponi, "Length of dark_files must be same as number of poni_files"

    opts.output_path = Path(opts.output_path)
    if opts.output_formats in ["fxye","xye"] and opts.units!="2th_deg":
        print("The fxye and xye gsas-ii output formats are only available in 2th_deg")
        opts.units = "2th_deg"
    return opts

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('true'):
        return True
    elif v.lower() in ('false'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

class Diffraction(object):
    """ Class that stores calibration settings for a single detector
    and the raw data.
    """

    def __init__(self, poni_file, data_ops, mask_file,
        bright_file=None,bright_norm=None,dark_file=None,dark_norm=None,norm_exposure=False,rot_offset=0,detector_name='generic'):

        # store input files
        self.poni_file = poni_file
        self.data_ops = data_ops.split(",")
        self.mask_file = mask_file
        self.bright = bright_file
        self.bright_norm = bright_norm
        self.dark = dark_file
        self.dark_norm = dark_norm
        self.darkbright=None
        self.detector_name = detector_name
        #print(detector_name)
        self.tif_loader = getattr(self,f"tif_loader_{self.detector_name}")
        self.norm_exposure = norm_exposure
        self.time = None
        self.time_reference = [None]*2
        self.exposure = [None]*2
        self.exposure_period = [None]*2

        # read some more information about calibration
        with open(self.poni_file) as fp:
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
                self.rot3 = float(value)+np.radians(rot_offset)
            elif name == "Wavelength":
                self.wavelength = float(value)

        # load, normalize, and sum bright/dark
        if bright_file is not None:
            bright_files = sorted([str(p) for p in Path().rglob(bright_file)])
            self.bright = self.load_and_process(bright_files,bright_norm,norm_exposure,False)
            self.darkbright = self.bright
        else:
            self.bright=None

        if dark_file is not None:
            dark_files = sorted([str(p) for p in Path().rglob(dark_file)])
            self.dark = self.load_and_process(dark_files,dark_norm,norm_exposure,False)
            if self.darkbright is None:
                self.darkbright=self.dark
            else:
                self.darkbright+=self.dark
        else:
            self.dark=None

        if mask_file:
            self.mask = self.apply_ops(fabio.open(mask_file).data)
        else:
            self.mask=None


    def load_and_process(self,data_file,norm,norm_exposure,isexp=True):
        data, exposure = self.tif_loader(data_file)
        data = self.normalize(data,norm,exposure,norm_exposure)
        data = self.sum_data(data)
        if isexp and self.darkbright is not None:
            data = data - self.darkbright
        data = self.apply_ops(data)
        return data

    def tif_loader_generic(self,files,data_type="int32"):
        # load operation
        data = []
        for file in files:
            fimage = PIL.Image.open(file)
            data.append(np.asarray(fimage,data_type))
        return data, [1.0]*len(data)

    def tif_loader_ge(self,files,data_type="int32"):
        o = GEimage.GeImage()
        
        # load operation
        data = []
        time = []
        time_reference = []
        exposure = [1,1] #hardcoded because we don't know the exposure tag 
        exposure_period=None
        o.read(fname=files[0])
        datatmp=np.zeros((),dtype=data_type)
        for file in files:
            o.read(fname=file)
            acq_step = 1.0/o.header['AcquisitionFrameRateInFps']
            acq_date = o.header['AcquisitionDate'].decode("ascii")[:11]
            acq_time = o.header['AcquisitionTime'].decode("ascii")[:8]
            acq_epoc = datetime.strptime(f"{acq_date},{acq_time}",'%d-%b-%Y,%H:%M:%S').timestamp()
            for index,frame in enumerate(o.frames()):
                time.append(acq_epoc+acq_step*index)
                time_reference.append(acq_epoc)
                datatmp=datatmp+np.asarray(frame.data,data_type)
            data.append(datatmp / o.nframes)

        self.time = self.sum_data(time)
        self.time_reference = [time_reference[0],time_reference[-1]]
        self.exposure = exposure 
        self.exposure_period = exposure_period
        return data, exposure

    def tif_loader_pilatus_1ID(self,files,data_type="int32"):
        # load operation
        data = []
        time = []
        time_reference = []
        exposure = []
        exposure_period = []
        for file in files:
            fimage = PIL.Image.open(file)
            tmp = fimage.tag_v2[270].split('\r\n')[2:4]
            exposure.append(float(tmp[0].split(' ')[-2]))
            exposure_period.append(float(tmp[0].split(' ')[-2]))
            time.append(float(f"{fimage.tag_v2[65002]}.{fimage.tag_v2[65003]}"))
            time_reference.append(float(fimage.tag_v2[65000]))
            data.append(np.asarray(fimage,data_type))
        
        self.time = self.sum_data(time)
        #print("time:", fimage.tag_v2[65002])
        self.time_reference = [time_reference[0],time_reference[-1]]
        self.exposure = [exposure[0],exposure[-1]]
        self.exposure_period = [exposure_period[0],exposure_period[-1]]
        return data, exposure

    def tif_loader_pixirad_1ID(self,files,data_type="int32"):
        # load operation
        data = []
        time = []
        time_reference = []
        exposure = [1,1] #hardcoded because we don't know the exposure tag 
        exposure_period = None
        for file in files:
            fimage = PIL.Image.open(file)
            time.append(float(f"{fimage.tag_v2[65002]}.{fimage.tag_v2[65003]}"))
            time_reference.append(float(fimage.tag_v2[65000]))
            data.append(np.asarray(fimage,data_type))

        self.time = self.sum_data(time)
        self.time_reference = [time_reference[0],time_reference[-1]]
        self.exposure = exposure
        self.exposure_period = exposure_period
        return data, exposure

    def normalize(self,data,norm,exposure,norm_exposure):
        if norm_exposure:
            for i, (d,e) in enumerate(zip(data,exposure)):
                data[i] = d / e / norm
        else:
            for i, d in enumerate(data):
                data[i] = d / norm
        return data

    def sum_data(self,data):
        return np.sum(data,axis=0) / len(data)

    def apply_ops(self,data: np.array):
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

    def get_header(self):
        header_elements=[]
        keys = ["time","time_reference","exposure","exposure_period"]
        for key in keys:
            header_elements.append(f"{key}: {self.__getattribute__(key)}")
        return header_elements
def cake2MAUD(i_2d,r_2d,chi_2d,mg,mask,min_count=5):
     ig = ext.invert_geometry.InvertGeometry(r_2d, chi_2d)
     
def cake2MAUD_old(i_2d,tth_2d,chi_2d,mg,mask,min_count=5):
    mg = mg.ais[0]
    mask=mask[0]
    #Compute the chi and tth angles for each pixel and apply mask
    chi=mg.chia.ravel()*180.0/np.pi
    tth=mg.ttha.ravel()*180.0/np.pi
    chi=np.ma.masked_array(chi,mask.ravel()).compressed()
    tth=np.ma.masked_array(tth,mask.ravel()).compressed()
    

    #Get position of each pixel in then untransformed detector frame 
    x=[]
    y=[]
    for xp in range(0,mg.get_shape()[0]):
        xtmp=xp*mg.pixel1-mg.poni1
        for yp in range(0,mg.get_shape()[1]):
            x.append(xtmp)
            y.append(yp*mg.pixel2-mg.poni2)

    posxy = np.empty(shape=[mg.get_shape()[0],mg.get_shape()[1],2])
    for ix in range(0,posxy.shape[0]):
        posxy[ix,:,0]=ix*mg.pixel1-mg.poni1
        for jy in range(0,posxy.shape[1]):
            posxy[ix,jy,1]=jy*mg.pixel2-mg.poni2

    #convert from m to mm and apply mask
    posxy=posxy*1e3
    x=np.ma.masked_array(posxy[:,:,0].ravel(),mask.ravel()).compressed()
    y=np.ma.masked_array(posxy[:,:,1].ravel(),mask.ravel()).compressed()


    #Compute the bins corresponding to cake angles
    bins_tth=tth_2d-(tth_2d[1]-tth_2d[0])/2.0
    bins_tth=np.append(bins_tth,tth_2d[-1]+(tth_2d[1]-tth_2d[0])/2.0)
    bins_chi=chi_2d-(chi_2d[1]-chi_2d[0])/2.0
    bins_chi=np.append(bins_chi,chi_2d[-1]+(chi_2d[1]-chi_2d[0])/2.0)

    #Get the mean position on the detector of each cake bin and the number of
    #contributing points for each bin
    x_mean_bins = stats.binned_statistic_2d(chi,tth, x, bins=[bins_chi,bins_tth],statistic='mean')[0]
    y_mean_bins = stats.binned_statistic_2d(chi,tth, y, bins=[bins_chi,bins_tth],statistic='mean')[0]
    counts_bins = stats.binned_statistic_2d(chi,tth, y, bins=[bins_chi,bins_tth],statistic='count')[0]

    #Create a bin level mask
    imask=np.ma.masked_invalid(x_mean_bins).mask | (i_2d==0) | (counts_bins<min_count)
    x_mean_bins_clean=np.ma.masked_array(x_mean_bins,imask)
    y_mean_bins_clean=np.ma.masked_array(y_mean_bins,imask)
    i_2d_clean=np.ma.masked_array(i_2d,imask)
    counts_bins_clean=np.ma.masked_array(counts_bins,imask)
    weights_2d_clean=1/np.sqrt(i_2d_clean)
    
    return i_2d_clean,x_mean_bins_clean,y_mean_bins_clean,counts_bins_clean,weights_2d_clean

def write_esg(i_2dm,x_2dm,y_2dm,weight_2dm,chi_2d,fname,mg):    
    mg = mg.ais[0]
    blockid=0
    
    f = open(fname, "w")    
    f.write("_pd_block_id noTitle|#%d\n" % (blockid))
    f.write("\n")
    f.write("_diffrn_detector 2D\n")
    f.write("_diffrn_detector_type CCD like\n")
    f.write("_pd_meas_step_count_time ?\n")
    f.write("_diffrn_measurement_method diffraction_image\n")
    f.write("_diffrn_measurement_distance_unit mm\n")
    f.write("_pd_instr_dist_spec/detc %f\n" % (mg.get_dist()*1e3))
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
    
    for i,chi in enumerate(chi_2d):
        intensities=i_2dm[i].compressed()
        if len(intensities)>0:
            xs=x_2dm[i].compressed()
            ys=y_2dm[i].compressed()
            weights=weight_2dm[i].compressed()
            f.write("_pd_block_id noTitle|#%d\n" % (blockid))
            f.write("\n")
            f.write("_pd_meas_angle_eta %f\n" % (chi))
            f.write("\n")
            f.write("loop_\n")
            f.write("_pd_meas_position_x _pd_meas_position_y _pd_meas_intensity_total\n")#" _pd_meas_intensity_sigma\n")
            for x, y, intensity, weight in zip(xs, ys, intensities, weights):
                f.write("%f %f %f\n" % (x,y,intensity))
            f.write("\n")
            blockid+=1
    f.close()    

def write_spectra(xradial,intensity,sigma,stem,fmt,chi,omega,header=[]):
    file = f"{stem}.{fmt}"
    header = deepcopy(header)
    header.insert(0,f"{file}")
    if fmt == 'fxye':
        header.append(f"BANK 1 {len(xradial)} {len(xradial)} CONS {xradial[0]} {xradial[1]-xradial[0]} 0 0 FXYE")
        np.savetxt(file,
            np.c_[100*xradial,intensity,sigma],
            delimiter='\t',
            header='\n'.join(header),
            comments='')
    elif fmt == 'xye':
        header = [f"# {h}" for h in header]
        header.insert(0,"/*")
        header.append("*/")
        np.savetxt(file,
            np.c_[xradial,intensity,sigma],
            delimiter='\t',
            header='\n'.join(header),
            comments='')
    elif fmt == 'xy':
        header = [f"# {h}" for h in header]
        header.insert(0,"/*")
        header.append("*/")
        np.savetxt(file,
            np.c_[xradial,intensity],
            delimiter='\t',
            header='\n'.join(header),
            comments='')
    elif fmt == 'xy-noheader':
        np.savetxt(file,
            np.c_[xradial,intensity],
            delimiter='\t',
            comments='')
    elif fmt == "esg":
        header = f"_pd_block_id noTitle|#0\n" \
                f"_pd_meas_angle_eta {chi}\n" \
                f"_pd_meas_angle_omega {omega}\n" \
                f"loop_\n" \
                f"_pd_meas_position_x _pd_meas_intensity_total"
        np.savetxt(file,
            np.c_[xradial,intensity],
            delimiter='\t',
            header=header,
            comments='')
    elif fmt == "esg2":
        return
    else:
        print("fmt is not yet implemented")                                
        raise NotImplementedError            

def get_files(data_file,dir_range,wild_range):
    if dir_range is not None:
        files = sorted([str(p) for p in Path().rglob(data_file)])
        files=files[dir_range[0]:dir_range[1]]
    elif wild_range is not None:
        for idx in range(wild_range[0],wild_range[1]+1):
            files=data_file.replace("*",f"{idx}")
    else:
        files=sorted([str(p) for p in Path().rglob(data_file)])
    
    return files

def get_averaging_sets(files,avg_window,strid):
    if avg_window>len(files):
        return [files],len(files)

    file_sets=[]
    window=np.array(list(range(0,avg_window+1))) 
    for i in range(0,len(files)-avg_window+1,strid):
        file_sets.append(files[i+window[0]:i+window[-1]])
    return file_sets

def initialize_detectors(opts):
    # load data and poni files
    detectors = []
    for poni_file, data_ops, mask_file, bright_file, dark_file in zip(opts.poni_files,
                                                                        opts.data_operations,
                                                                        opts.mask_files,
                                                                        opts.bright_files,
                                                                        opts.dark_files
                                                                        ):
        detectors.append(Diffraction(poni_file, 
                            data_ops,
                            mask_file,
                            bright_file,
                            opts.bright_norm,
                            dark_file,
                            opts.dark_norm,
                            opts.norm_exposure_meta,
                            opts.rot_offset,
                            opts.detector_name
                        ))    
    return detectors

def initialize_integrator(detectors,opts):
    # load calibration
    mg = multi_geometry.MultiGeometry(
            [detector.poni_file for detector in detectors],
            unit=opts.units,
            radial_range=opts.radial_range,
            azimuth_range=opts.azimuth_range)
    return mg

def spectra_stem(image_file,opts):
    if opts.avg_window==1:
        stem = opts.output_path / f"{Path(image_file[0]).stem}{opts.output_postfix}"
    else:
        stem = opts.output_path / f"{Path(image_file[0]).stem}_{Path(image_file[-1]).stem.split('_')[-1]}{opts.output_postfix}"
    return stem

def integrate(detectors,opts,image_files):
    stem = spectra_stem(image_files[0],opts)

    if not opts.overwrite and all([Path(f"{stem}.{of}").is_file() for of in opts.output_formats]):
       #Nothing to do
       return

    #Get data   
    data=[]
    for images,detector in zip(image_files,detectors):
        data.append(detector.load_and_process(images,opts.norm,opts.norm_exposure_meta))

    #Get mask 
    mask = [detector.mask for detector in detectors]

    #Get spetra header 
    header = detectors[0].get_header()

    #Construct integrators
    mg = initialize_integrator(detectors,opts)
    # mg = pyFAI.load(detectors[0].poni_file) 

    if opts.npt_azim==1 and not opts.force_2dintegrator:
        integration1d(mask,mg,data,opts,stem,header)
    else:
        integration2d(mask,mg,data,opts,stem,header)

def integration1d(mask,mg,data,opts,stem,header):
    #Integrate
    xradial,intensity,sigma = mg.integrate1d(lst_data=data,
                                npt=opts.npt_radial,
                                lst_mask=mask,
                                polarization_factor=opts.polarization_factor,
                                method=opts.method,
                                error_model=opts.error_model,
                                correctSolidAngle=opts.correctSolidAngle)

    #Clean empty bins optional
    if opts.remove_empty_bins:
        intensity[intensity==0]=np.nan 

    #Output optional
    for output_format in opts.output_formats:
        write_spectra(xradial,intensity,sigma,stem,output_format,0.0,opts.omega_rot,header=header)

def integration2d(mask,mg,data,opts,stem,header):
    #Integrate
    intensitys,xradial,azimuths = mg.integrate2d(lst_data = data,
                npt_rad=opts.npt_radial,
                npt_azim=opts.npt_azim,
                lst_mask=mask,
                polarization_factor=opts.polarization_factor,
                method=opts.method,
                error_model=opts.error_model,
                correctSolidAngle=opts.correctSolidAngle)
    
    #Write the spectra
    if "esg2" in opts.output_formats:
        i_2dm,x_2dm,y_2dm,count_2dm,weight_2dm = cake2MAUD(intensitys,xradial,azimuths,mg,mask,min_count=1)
        write_esg(i_2dm,x_2dm,y_2dm,weight_2dm,azimuths,f"{stem}.esg",mg)

    include = np.full(opts.npt_radial, True)
    for intensity,azimuth in zip(intensitys, azimuths):
        if opts.remove_empty_bins:
            include = intensity!=0 
        chi = np.round(azimuth+opts.rot_offset,1)
        stemazim = f"{stem}_azim_{np.round(azimuth+opts.rot_offset,1)}"
        sigma = intensity*0
        if len(xradial[include])!=0:
            for output_format in opts.output_formats:
                write_spectra(xradial[include],intensity[include],sigma[include],stemazim,output_format,chi,opts.omega_rot,header=header)

def main():
    #Get arguments from user
    opts=get_arguments()

    #Build detector objects from poni and opts
    detectors = initialize_detectors(opts)

    # #Construct integrators
    # mg = initialize_integrator(detectors,opts)

    for detector_id,data_files in enumerate(opts.data_files):
        #Construct file list and incorporate any filtering
        images = get_files(data_files,
                                opts.dir_range,
                                opts.wild_range)
        #Construct file sets for averaging 
        image_groups = get_averaging_sets(images,
                                            opts.avg_window,
                                            opts.strid)
        print(image_groups)
        #Group sets by detector
        # if detector_id==0:
        #     image_sets = [[[]]*len(detectors)]*len(image_groups)
        for group_id,image_group in enumerate(image_groups):
            image_groups[group_id]=[image_groups[group_id]]
        print(image_groups)
    # for i,image in enumerate(image_sets):
    #     image_sets[i] = image_sets[0]

    #ensure output directory is there
    opts.output_path.mkdir(exist_ok=True)
    print("")
    print(f"Using {opts.pool_size} of {os.cpu_count()} cpus.")
    print(f"File input is {opts.data_files}")
    print(f"Output directory is {opts.output_path}")
    print(f"The file formats {opts.output_formats} will be exported")
    print(f"Running integration with {opts.avg_window} window width and {opts.strid} strid")
    # integrate(detectors,opts,image_groups[0])

    with Pool(opts.pool_size) as pool:
        list(tqdm.tqdm(pool.imap(partial(integrate,detectors,opts),image_groups),total=len(image_groups)))

if __name__ == "__main__":
    freeze_support()
    main()