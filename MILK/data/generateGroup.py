#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 14:38:43 2020

@author: danielsavage
"""
import os
import argparse
from . import prepareData

class group:
    def __init__(self):
        self.filename=None
        self.run_dirs=None
        self.ifile=None
        self.ofile=None
        self.data_dir=None
        self.data_range=None
        self.data_groupsz=None
        self.ext=None
        self.args=None
    def parseConfig(self,config,run_dirs=None,ifile=None,ofile=None,data_dir=None,data_range=None,data_groupsz=None,ext=None,filename='groupDatasets.txt'):
                   
        if run_dirs==None: 
            self.run_dirs=config.folders.run_dirs
        else:
            self.run_dirs=run_dirs
            
        if ifile==None: 
            self.ifile=config.ins.riet_analysis_file 
        else:
            self.ifile=ifile
            
        if ofile==None:
            self.ofile=config.ins.riet_analysis_fileToSave
        else:
            self.ofile=ofile

        if data_dir==None:
            if config.datatype.data_format=='HIPPO':
                self.data_dir=config.hippo.data_dir
        else:
            self.data_dir=data_dir
            
        if data_range==None: 
            if config.datatype.data_format=='HIPPO':
                self.data_range=config.hippo.data_range
        else:
            self.data_range=data_range
            
        if data_groupsz==None:
            if config.datatype.data_format=='HIPPO':
                self.data_groupsz=str(len(config.hippo.chi_meas))
        else:
            self.data_groupsz=data_groupsz
            
        if ext==None:
            if config.datatype.data_format=='HIPPO':
                self.ext='.gda'
        else:
            self.ext=ext
            
        self.filename=filename
        
    def generateGroup(self):
        self.parse_arguments()
        main(self.args)
        
    def prepareData(self):
        prepareData.main('-fn '+self.filename)
        
    def parse_arguments(self):
        args=''
        if self.run_dirs!=None:
            args=args+'--run_dirs '+self.run_dirs+' '
        if self.ifile!=None:
            args=args+'--ifile '+self.ifile+' '
        if self.ofile!=None:
            args=args+'--ofile '+self.ofile+' '
        if self.data_dir!=None:
            args=args+'--data_dir '+self.data_dir+' '
        if self.data_range!=None:
            args=args+'--data_range '
            for r in self.data_range:                
                args=args+str(r[0])+' '+str(r[1])+' '
        if self.data_groupsz!=None:
            args=args+'--data_groupsz '+self.data_groupsz+' '
        if self.ext!=None:
            args=args+'--ext '+self.ext+' '
        if self.filename!=None:
            args=args+'--file_name '+self.filename+' '

        #trim at the end
        self.args=args[0:-1]
        
def write_groupDatasets(args):
        
    #Generate the working directory
    root = os.getcwd()    
         
    fname=os.path.join(root,args.file_name)
    fID = open(fname, "w")
    
    #write cif loop header
    fID.write('DataDir RunDir template.par output.par dataset1 dataset2 datasets3...\n')
    
    linind=0
    for ind in range(0,int(len(args.data_range)/args.data_groupsz)):
        fID.write('%s %s %s %s ' % (args.data_directory,args.run_dirs.replace('(wild)',str(ind).zfill(3)), args.ifile,args.ofile))
        for data in range(0,args.data_groupsz):
            fID.write('%s ' % (str(args.data_range[linind])+args.ext))
            linind=linind+1
        fID.write('\n')

def get_arguments(argsin):
    #Parse user arguments
    welcome = "This is an interface generates a groupFile that can be manually adjusted for initializing data"
    
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--ifile', '-i', required=True, 
                        help='The input parameter file used as a starting point for the batch analysis. e.g. Initial.par')
    parser.add_argument('--ofile', '-o', 
                        help='A .par file name for all analysis to be saved to e.g. Initial_(wild).par or Initial.par. In the case that wild is not specified all analysis will be saved with same name but in the directory(s) specified by sub folder')
    parser.add_argument('--file_name', '-fn', default='groupDatasets.txt',  
                        help='Output file name with the groupedDatatsets')
    parser.add_argument('--data_directory', '-dd',  
                        help='Directory where datasets reside')
    parser.add_argument('--data_range', '-dr', required=True,type=int, nargs='+', 
                        help='specify a range of datasets to populate the file with')
    parser.add_argument('--run_dirs', '-rd', default='runwild', 
                        help='The dataset directories e.g. runwild/shock')
    parser.add_argument('--data_groupsz', '-dg',type=int, default=3,
                        help='Specify the number of rotations to group')
    parser.add_argument('--ext', '-e', default='.gda',
                        help='Specify the extension of the gda')

    if argsin==[]:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argsin.split(' '))
    
    data_range=[]
    for pair in range(0,len(args.data_range),2):      
        tmp_id=range(args.data_range[pair],args.data_range[pair+1]+1)
        for i in tmp_id:
            data_range.append(i)
    setattr(args, 'data_range', data_range)
    
    if args.ofile==None:
        args.ofile=args.ifile
    
    if 'wild' not in args.run_dirs:
        args.run_directory=args.run_dirs+'(wild)'
    
    assert len(args.data_range) % args.data_groupsz == 0, 'The data range you specified is not divisable by the number of data_groups'
    
    return args
    
def main(argsin):
    args=get_arguments(argsin)
    write_groupDatasets(args)
    
if __name__ == '__main__':
    #Get arguments from user
    main([])
