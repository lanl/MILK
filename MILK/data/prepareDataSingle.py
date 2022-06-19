#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 14:46:33 2020

@author: danielsavage
"""
import argparse
import os

def read_file(ifile):
    with open(ifile) as f:
        lines = f.readlines()
    return lines

def write_file(lines,ofile):
    with open(ofile, 'w') as f:
        f.writelines("%s\n" % line.strip() for line in lines)

def remove_intensity(lines):
    indStart=[]
    indEnd=[]    
    for ind in range(0,len(lines)):
        line=lines[ind]
        if "#custom_object_intensity_data" in line:
            indStart.append(ind)
        
        if "#end_custom_object_intensity_data" in line:
            indEnd.append(ind+1)
    
    #Remove in reverse order
    for ind in reversed(range(0,len(indStart))):
        del lines[indStart[ind]:indEnd[ind]]
            
    return lines

def swap_datasets(lines,datasets):

    #Get the extension of the datasets we are swapping in 
    ext=datasets[0].split('.')[-1]
    #Find a list of datasets already in the template
    datasetsold=[]
    datasetInd=[]
    for ind in range(0,len(lines)):
        line=lines[ind]
        if ext in line: 
            datasetInd.append(ind)
            tmp=line.split('_')[-1]
            tmp=tmp.split(' ')[-1]
            tmp=tmp.replace("'",'')
            datasetsold.append(tmp.split('.')[0]+'.'+ext)
        
    #Get the unique datasets make sure datasets make sense
    datasetsold = sorted(set(datasetsold))
    assert len(datasetsold)==len(datasets),'The length of datasets were not the same!'
    
    #Loop over the datasets and copy in the new file names 
    for ind in datasetInd:
        line=lines[ind]
        for ind2 in range(0,len(datasetsold)):
            if datasetsold[ind2] in line:
                line=line.replace(datasetsold[ind2],datasets[ind2])
        lines[ind]=line
    return lines

def get_arguments():
    #Parse user arguments
    welcome = "This is a program for batch preperation of data and MAUD datasets\
               for .gda, .esg, or other extensions where the data frame can be\
               read into a template."
    
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--dir', '-d', 
                        help='Relative path to directory to apply modifications to')
    parser.add_argument('--ifile', '-i', required=True,
                        help='Define input file as template ')
    parser.add_argument('--ofile', '-o', 
                        help='Define output parameter file to save to (default is input file) ')
    parser.add_argument('--datasets', '-l', nargs='+',action='append',required=True,
                        help='Specify list of sequential gda to replace')
    parser.add_argument('--keepInt', '-r', default=False,
                        help='Specify whether the intensity should be kept in the parameter file (default: False)')

    parser.parse_args()    
    args = parser.parse_args()
    
    #Set the working directory
    if args.dir==None:
        args.dir = os.getcwd()
    else:
        args.dir = os.path.join(os.getcwd(),args.dir)
    
    if args.ofile==None:
        args.ofile = args.ifile
    
    args.datasets=args.datasets[0]
    
    return args

if __name__ == '__main__':
    #Get arguments from user
    args=get_arguments()
    
    #read template file
    lines = read_file(args.ifile)
    
    #Remove intensity data if appropriate 
    if not args.keepInt:
        lines=remove_intensity(lines)
    
    #detect the current dataset names and replace with new dataset names 
    lines=swap_datasets(lines,args.datasets)
    
    #Write the parameter file to the directory
    write_file(lines,args.ofile)