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
    parser.add_argument("--step", nargs="+", required=True,
        help="options a step from Rietveld.")
    parser.add_argument("--dataset",type=str,default=None,help="Specify e.g. dataset.csv (default to run number).")
    parser.add_argument("--dependent_var",type=str,default="dataset.csv")
    parser.add_argument("--spectra_label",type=str,default="d(angstrom)")
    parser.add_argument("--radial-range", nargs=2, type=float, default=None)
    opts = parser.parse_args()

    return opts

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
        data_lines = lines[nheader:]
        for line in data_lines:
            data = line.split('\t')
            x.append(float(data[0])/100)
            y.append(float(data[1]))
            # sigma.append(float(data[2]))
    return x,y,sigma,time      

def get_files(data_files,dir_range,wild_range):


def main():
    #Get arguments from user
    opts=get_arguments()

    dataset = pd.read_csv(opts.dataset)
    wild = [i for i, x in enumerate(dataset["run"]) if x]


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