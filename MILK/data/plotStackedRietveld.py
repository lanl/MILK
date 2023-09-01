#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 16:08:30 2023

@author: ZhangxiFeng
"""

import numpy as np
import matplotlib.pyplot as plt
import argparse

class Plot_Rietveld():
    """A class used for plotting 3 Rietveld result plots stacked on top of each other. The three plots are:
    1. Diffraction data with refined fit.
    2. D-spacing positions of the peaks of the phases.
    3. Difference between the data and the fit.
    
    Required inputs:
        - rootFolder = a string of the folder to to look for data, i.e. 'run001' that exists in the current working folder.
        - filename = a string of the name of the file that contains the diffraction data, printed by MAUD, typically named 'all_spectra.cif'
        - wavelength = wavelength of the diffraction source, used to calculate d-spacing from 2-theta
        - headerlines = number of header lines in "filename", typically 21
        - columns = number of columns of data in "filename", typically 10
        - HKLFileNames = an array of strings that contains the HKL file names, i.e. ['alphaHKL.txt','steelHKL.txt','betaHKL.txt']
        - headerlinesHKL = number of header lines in the HKL files, typically 13
        - columnsHKL = number of columns of data in the HKL files, typically 8
        - HKLdSpacingColumn = the column in the HKL file that has the value of the d-spacing to be plotted, typically 6
        - HKLtextXoffset = the distance offset to place the text that labels the phase, i.e. [0.37, 0.42, 0.37]
        - HKLVPosition = the vertical position to place the text and the bars, i.e. [0.04, 0.12, 0.2]
        - HKLbarHalfLength = the half length of the bar. The bars will be plotted at the full length, i.e. 0.02
        - subStepFolder = any sub-folders for finding "filename", i.e. 'step_2' for 'run001/step_2/all_spectra.cif'
        - HKLLabel = the label of each HKL plot, raw strings allowed, i.e. HKLLabel = [r"$\alpha$","steel",r"$\beta$"]
        - dataColumn = the column in "filename" that has the values for the diffraction data, typically 5
        - fitColumn = the column in "filename" that has the values for the Rietveld fit, typically 6
        - height = height of the overall figure
        - width = width of the overall figure
        - fontsize = fontsize to be used in the figure
    Example Usage:
    import MILK
    plotClass = MILK.plotStackedRietveld.Plot_Rietveld(rootFolder=rootFolder[foldIndx][0],filename='all_spectra.cif',wavelength=0.1839,headerlines=21,columns=10,
            headerlinesHKL=13,columnsHKL=8,HKLFileNames=['alphaHKL.txt','steelHKL.txt','betaHKL.txt'],
            HKLdspacingColumn=6, HKLtextXoffset=[0.37,0.42,0.37], HKLVPosition=[0.04,0.12,0.2],
            HKLbarHalfLength=0.02,HKLLabel=[r"$\alpha$","steel",r"$\beta$"],
            subStepFolder=subStepFolder[foldIndx][0],dataColumn=5,fitColumn=6,height=3.25,width=1.3,fontSize=6)
    """
    def __init__(self,rootFolder=None,filename=None,wavelength=0.18,headerlines=21,columns=10,
                 HKLFileNames=None,headerlinesHKL=13,columnsHKL=8,HKLdSpacingColumn=6,
                 HKLtextXoffset=None,HKLVPosition=[],HKLbarHalfLength=0.02,HKLLabel=None,
                 subStepFolder=None,dataColumn=5,fitColumn=6,height=3.25,width=1.3,fontSize=6):
        self.rootFolder = rootFolder
        self.filename = filename
        self.wavelength = wavelength
        self.headerlines = headerlines
        self.columns = columns
        self.HKLFilenames = HKLFileNames
        self.headerlinesHKL = headerlinesHKL
        self.columnsHKL = columnsHKL
        self.HKLs = []
        self.HKLdspacingColumn = HKLdSpacingColumn
        self.HKLtextXoffset = HKLtextXoffset
        self.HKLVPosition = HKLVPosition
        self.HKLbarHalfLength = HKLbarHalfLength
        self.HKLLabel = HKLLabel
        self.subStepFolder = subStepFolder
        self.dataColumn = dataColumn
        self.fitColumn = fitColumn
        self.height = height
        self.width = width
        self.fontSize = fontSize
        self.dSpacing = []
        self.diffIntensTotalCalc = []

    def read_Spectra_Files(self):
        # read data from file with header removed
        with open(self.rootFolder + '/' + self.subStepFolder + '/' + self.filename, 'r') as the_file:
            all_data = [line.strip() for line in the_file.readlines()]
            data = all_data[self.headerlines:]
            data = [list(map(float, row.split())) for row in data]

        # read the number of rows of entry in the file
        rows = len(data)
        self.spectra = np.zeros([rows,self.columns])
        # convert the data to array for easier manipulation
        for i in range(rows):
            self.spectra[i][:] = data[i][0:self.columns]

    def read_HKL_Files(self,HKLfname):
        # read data from file with header removed
        with open(self.rootFolder + '/' + HKLfname, 'r') as the_file:
            all_data = [line.strip() for line in the_file.readlines()]
            data = all_data[self.headerlinesHKL:]
            data = [list(map(float, row.split())) for row in data]

        # read the number of rows of entry in the file
        rows = len(data)
        HKLs = np.zeros([rows,self.columnsHKL])

        # convert the data to array for easier manipulation
        for i in range(rows):
            HKLs[i][:] = data[i][0:self.columnsHKL]
        
        return HKLs

    def plot_Stacked_Rietveld(self):
        
        self.read_Spectra_Files()
        twoTheta = self.spectra[:,0]
        self.dSpacing = self.wavelength/(2*np.sin(np.deg2rad(twoTheta/2)))
        self.diffIntensTotalCalc = (self.spectra[:,self.dataColumn] - self.spectra[:,self.fitColumn])
        for i in range(len(self.HKLFilenames)):
            self.HKLs.append(self.read_HKL_Files(self.HKLFilenames[i]))

        fig = plt.figure(figsize=(self.height,self.width))
        gs = fig.add_gridspec(3,1,hspace=0, wspace=0,height_ratios=[2,1,1])

        plt.rcParams['font.size'] = str(self.fontSize)

        (ax1,ax2,ax3) = gs.subplots(sharex='col')

        ax1.plot(self.dSpacing, self.spectra[:,self.dataColumn], linestyle="None", marker='+', markersize=2.5, fillstyle='none',markeredgewidth=0.3,color='blue', label='Data')
        ax1.plot(self.dSpacing, self.spectra[:,self.fitColumn], linewidth=0.8, color='red', label='Fit')

        ax1.set_ylim(bottom=0)
        ax1.tick_params(bottom=False,labelbottom=False)
        # ax1.set_xticklabels([])
        ax1.set_ylabel(r'Intensity',fontsize=6)
        ax1.legend(loc='best',fancybox=False,framealpha=0.0,fontsize=6)

        for i in range(len(self.HKLs)):
            ax2.text(self.dSpacing[-1]-self.HKLtextXoffset[i], self.HKLVPosition[i], self.HKLLabel[i], fontsize=6)
            for j in range(len(self.HKLs[i])):
                ax2.plot([self.HKLs[i][j,self.HKLdspacingColumn],self.HKLs[i][j,self.HKLdspacingColumn]], 
                         [self.HKLVPosition[i]-self.HKLbarHalfLength,self.HKLVPosition[i]+self.HKLbarHalfLength], linewidth=0.3, color='black')
        ax2.set_ylim([0,0.26])

        ax2.tick_params(left = False, bottom = False, labelbottom=False,labelleft=False)

        ax3.plot(self.dSpacing,self.diffIntensTotalCalc,linewidth=0.8,color='black')

        # ax3.set_ylim([-0.1,0.3])
        ax3.set_xlabel(r'D-spacing ($\AA$)',fontsize=6)
        ax3.set_ylabel(r'$\Delta$',fontsize=6)
        ax3.tick_params(bottom=True,left=True,labelbottom=True)

        fig.savefig(self.rootFolder+'stackedPlot.pdf',bbox_inches='tight',transparent=True)