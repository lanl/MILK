#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 17:07:51 2020

@author: danielsavage
"""


import argparse
import os

    
def get_arguments(argsin):
    #Parse user arguments
    welcome = "This is an interface appending a phase as exported from MAUD. Can \
        include things like stress, ODF, and other models. Import: CIF file must \
        be exported from MAUD since this script does not parse a standard cif file."
    
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--dir', '-d', 
                        help='Relative path to directory to apply modifications to')
    parser.add_argument('--ifile', '-i', required=True, 
                        help='par file to which the phase information is appended')
    parser.add_argument('--ofile', '-s',
                        help='A .par file name for saving')
    parser.add_argument('--afile', '-a', required=True, 
                        help='CIF to add (Must be exported from MAUD!)')
    if argsin==[]:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argsin.split(' '))

    #Set the working directory
    if args.dir==None:
        args.dir = os.getcwd()
    else:
        args.dir = os.path.join(os.getcwd(),args.dir)
    
    #Walk the directory to find par files to modify
    ifile=[]
    for cdir, dirs, files in os.walk(args.dir, topdown=False):
        for f in files:
            if args.ifile == f:
                ifile.append(os.path.join(cdir, args.ifile))
    args.ifile=ifile

    #Generate the output file names
    if args.ofile==None:
        args.ofile = args.ifile
    else:
        ofile=[]
        for file in args.ifile:
            ofile.append(os.path.join(os.path.dirname(file),args.ofile) )
        args.ofile=ofile    
    
    args.afile=os.path.join(os.getcwd(),args.afile)
    
    return args

def merge_files(ifile,afile,ofile):
    
    data = data2 = "" 
      
    # Reading data from file1 
    with open(ifile) as fp: 
        data = fp.read() 
      
    # Reading data from file2 
    with open(afile) as fp: 
        data2 = fp.readlines() 
    
    #Need to change one line for import of cif file to work 
    for ind,line in enumerate(data2):
        if 'data_phase' in line:
            phname=line.replace('data_phase_', '')
            data2[ind]='_pd_phase_name \'' + phname.strip()+'\'\n\n'
    
    data2.insert(0,'#subordinateObject_'+phname+'\n')
    data2.append('#end_subordinateObject_'+phname+'\n')

    
    # Merging 2 files 
    # To add the data of file2 
    # from next line 
    data += "\n"
    for line in data2:
        data += line 
      
    with open (ofile, 'w') as fp: 
        fp.write(data) 
def main(argsin):
    #Get arguments from user
    args=get_arguments(argsin)
    
    for i in range(0,len(args.ifile)): 
        merge_files(args.ifile[i],args.afile,args.ofile[i])

if __name__ == '__main__':
    main([])
       
