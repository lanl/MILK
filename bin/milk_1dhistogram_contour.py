import argparse
from functools import partial
from multiprocessing import Pool, freeze_support
# import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
# import fabio
# import PIL
import numpy as np
from pathlib import Path
import math
# import pyFAI
# from pyFAI.multi_geometry import MultiGeometry
from tqdm import tqdm
import os
import imageio
import pandas as pd

def get_arguments():
    #Parse user arguments
    welcome = "Commandline integration tool for 2D tifs with averaging."
    
    # parse command line
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument("--data-files", nargs="+", required=False,
        help="options are fxye, xye, xy, xy-noheader and multiple options can be specified.")
    parser.add_argument("--meta-file",type=str,default="meta.csv")
    parser.add_argument("--dir-range", nargs="+", type=int, default=None)
    parser.add_argument("--wild-range", nargs="+", type=int, default=None)
    parser.add_argument("--output-path", type=str, default=Path.cwd())
    parser.add_argument("--output-postfix", type=str, default="")  
    parser.add_argument("--output-formats", nargs="+", default=["xye"],
        help="options are fxye, xye, xy, xy-noheader and multiple options can be specified.")
    parser.add_argument("--units", choices=["2th_deg", "2th_rad", "q_nm^-1","q_A^-1", "r_mm"], default="2th_deg")
    parser.add_argument("--wave_length",type=float,default=None)
    parser.add_argument("--radial-range", nargs=2, type=float, default=None)
    parser.add_argument("--overwrite", type=str2bool, default=True)
    parser.add_argument("--cleanup",type=str2bool,default=False)
    parser.add_argument("--pool-size",type=int,default=os.cpu_count())

    opts = parser.parse_args()

    #testing block 
    opts.data_files = ['analysis/SamA_heating_insitu/caked_all/*.xy']
    opts.meta_file = "analysis/SamA_heating_insitu/meta.csv"
    # opts.poni_files = ["cal_washer_sunday_evening2.poni"]
    # opts.mask_files = ["mask_stuck_pixels.edf"]
    # opts.output_formats = ["fxye"]
    opts.output_path = Path("analysis/SamA_heating_insitu/")
    opts.dir_range = [0,1000]
    # opts.npt_radial = 2500
    # opts.radial_range = [2,12]
    # opts.strid=1
    # opts.avg_window=20
    # opts.norm=1
    # opts.npt_azim=1
    # opts.rot_offset=-7.5
    # opts.detector_name="pilatus_1ID"
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

def save_spectra_image(x,intensity,time,temperature,stem):
    fig = plt.figure()
    plt.plot(x,np.sqrt(intensity),linestyle='-', marker='+',markersize=3, color='k')
    plt.xlim([1,3.5])
    plt.ylim([0,np.sqrt(10000)])
    plt.xlabel(r'd-spacing ($/angstrom$)')
    plt.ylabel('sqrt(Intensity) arb units')
    plt.title(f"{stem.stem}, time: {time} sec")
    fig.savefig(stem,format='png',dpi=150)
    plt.close()

def load_spectra(file):
    fmt = file.split('.')[-1]
    if fmt == 'fxye' or fmt == 'xye' or fmt == 'xy':
        nheader=7
    elif fmt == 'xy-noheader':
        nheader=0
    else:
        raise argparse.ArgumentTypeError('Unsupported data type.')

    x=[]
    y=[]
    sigma=[]
    time=None
    with open(file,'r') as f:
        lines = f.readlines()
        # if nheader >2:
        #     time = float(lines[1].split(':')[-1])
        # else:
        #     time = None

        data_lines = lines[nheader:]
        for line in data_lines:
            data = line.split('\t')
            x.append(float(data[0])/100)
            y.append(float(data[1]))
            # sigma.append(float(data[2]))
    return x,y,sigma,time      

def get_files(data_files,dir_range,wild_range):
    if dir_range is not None:
        for data_file in data_files:
            files_tmp = sorted([str(p) for p in Path().rglob(data_file)])
            files = files_tmp[dir_range[0]:dir_range[1]]
    elif wild_range is not None:
        files=[]
        for data_file in data_files:
            for idx in range(wild_range[0],wild_range[1]+1):
                files.append(data_file.replace("*",f"{idx}"))
    else:
        for data_file in data_files:
            files=sorted([str(p) for p in Path().rglob(data_file)])
    
    return files

def plot_histogram1d(ofile,x,z,time,temperature):
   save_spectra_image(x,z,time,temperature,ofile)

def calc_dspacing(ttheta: np.array,wavelength: float):
    return wavelength/(2*np.sin(np.radians(ttheta)/2))    

def main():
    #Get arguments from user
    opts=get_arguments()

    df = pd.read_csv(opts.meta_file)

    # integrated_files = get_files(opts.data_files,
    #                         opts.dir_range,
    #                         opts.wild_range)

    integrated_files = df.name.array

    x,_,_,time_ref = load_spectra(f"analysis/SamA_heating_insitu/caked_all/{integrated_files[0]}") 
    x = calc_dspacing(np.array(x)*100,0.1305)                       
    #n_test = 1000
    z=[]
    t=[]
    for file in integrated_files:
        _,ztmp,_,_ = load_spectra(f"analysis/SamA_heating_insitu/caked_all/{file}")
        z.append(ztmp)
        # t.append(time_tmp-time_ref)
    # for file in integrated_files:
        #  plot_histogram1d(opts,time_ref,file)
    # build gif

    # fig = plt.figure()
    # plt.plot(x,np.log(z[0]),linestyle='-', marker='+',markersize=3, color='k')
    # plt.xlim([1.0,3.4])
    # plt.ylim([5.4,9.5])
    # plt.xlabel(r'd-spacing ($\AA$)')
    # plt.ylabel('Log Intensity (arb. units)')
    # plt.close()


    fig = plt.figure()
    levels = np.linspace(10.4,11.9,15)
    # im = plt.contourf(x, df.time.array, np.log(np.sqrt(z)),15,cmap=cm.gnuplot)
    im = plt.contourf(x, df.time.array, np.log(np.sqrt(z)),levels=levels,cmap=cm.gnuplot)
    #plt.yscale('log')
    plt.xlabel(r'd-spacing ($\AA$)')
    plt.ylabel(r"Time (seconds)")
    # plt.ylim(0, 1500)
    plt.xlim(1.95,3.71)
    #plt.title("Weld 33")
    cbar = fig.colorbar(im)
    cbar.ax.set_ylabel('Log Intensity (arb. units)')
    fig.savefig(f"{opts.output_path}/time_intensity2d_all.png",format='png',dpi=600)
    plt.close()

    fig,ax = plt.subplots()
    plt.plot(df.temp_tc.array,df.time.array,linestyle='-', marker='+',markersize=3, color='k')
    x_left, x_right = ax.get_xlim()
    y_low, y_high = ax.get_ylim()
    ratio=1.5
    ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio)
    plt.xlabel(r'Temperature TC, C')
    plt.ylabel(r'Time (seconds)')
    fig.savefig(f"{opts.output_path}/time_intensity2d_temperature.png",format='png',dpi=600)
    plt.close()

    # os.makedirs(str(opts.output_path / "histograms"),exist_ok=True)
    # for file in integrated_files:
         
    #      save_spectra_image(x,z,df.time.array,df.temp_tc.array,f"{opts.output_path / "histograms"}/.png")
    # build gif
    # with imageio.get_writer(opts.output_path / 'weld_33.gif', mode='I') as writer:
    #     for file in integrated_files:
    #         image = imageio.imread(opts.output_path / f"{Path(file).stem}.png")
    #         writer.append_data(image)



if __name__ == "__main__":
    freeze_support()
    main()