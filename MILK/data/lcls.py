#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 13:00:32 2020

@author: danielsavage
"""
import os
import shutil
import argparse

class group:
    def __init__(self):

        self.ifile=None
        self.ofile=None
        self.wild=None
        self.wild_range=None
        self.data_dir_in=None
        self.data_dir_out=None
        self.group_name=None
        self.remove_nmaud=None
        self.args=None

    def parseConfig(self,config,ifile=None,ofile=None,data_dir_in=None,data_dir_out=None,wild=None,wild_range=None,group_name=None,remove_nmaud=False):
                   
        if ifile!=None:
            self.ifile=ifile
        else: 
            self.ifile=config.lcls.template_name
            
        if ofile!=None:
            self.ofile=ofile
        else: 
            self.ofile=config.ins.riet_analysis_file    
            
        if data_dir_in!=None:
            self.data_dir_in=data_dir_in
        else:   
            self.data_dir_in=config.lcls.data_dir
        
        if data_dir_out!=None:
            self.data_dir_out=data_dir_out
        else:
            if '/' in config.lcls.data_dir:
                self.data_dir_out=config.lcls.data_dir.split('/')[-1]
            elif '(wild)' in config.lcls.data_dir:
                self.data_dir_out='run(wild)'
        
        if wild!=None:    
            self.wild=wild
        else:
            self.wild=config.folders.wild
        
        if wild_range!=None:    
            self.wild_range=wild_range
        else:
            self.wild_range=config.folders.wild_range
        
        if group_name!=None:    
            self.group_name=group_name
        else:
            self.group_name=config.lcls.group_name
            
        self.remove_nmaud=remove_nmaud   
       
    def prepareData(self):
        self.parse_arguments()
        main(self.args)
               
    def parse_arguments(self):
        args=''

        if self.ifile!=None:
            args=args+'--ifile '+self.ifile+' '
        if self.ofile!=None:
            args=args+'--ofile '+self.ofile+' '
        if self.data_dir_in!=None:
            args=args+'--data_dir_in '+self.data_dir_in+' '
        if self.data_dir_out!=None:
            args=args+'--data_dir_out '+self.data_dir_out+' '
        if self.wild!=None and self.wild!=[]:
            args=args+'--wild '
            for wild in self.wild:
                args=args+str(wild)+' '            
        if self.wild_range!=None and self.wild_range!=[[]]:
            args=args+'--wild_range '
            for wild_range in self.wild_range:
                args=args+str(wild_range[0])+' '+str(wild_range[1])+' '
        if self.remove_nmaud!=None:
            args=args+'--remove_NMAUD '+str(self.remove_nmaud)+' '                 
        if self.group_name!=None:
            args=args+'--group_name '
            for group in self.group_name:
                args=args+group+' '

        #trim at the end
        self.args=args[0:-1]



def get_arguments(argsin):
    #Parse user arguments
    welcome = "This script moves matching files from one folder to anther \
        work folder and groups unique datasets based on the LCLS format."
    
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--ifile', '-i', required=True,
                        help='path to raw data directory where each data set is in a run### folder')
    parser.add_argument('--ofile', '-o', required=True,
                        help='path to raw data directory where each data set is in a run### folder')
    parser.add_argument('--data_dir_in', '-din', required=True,
                        help='path to raw data directory where each data set is in a run### folder')
    parser.add_argument('--data_dir_out', '-dout', required=True,  
                        help='path to copy raw data to')
    parser.add_argument('--wild', '-n', type=int, nargs='+',
                        help='used with sub_folder (wild) e.g. 1 3 5 would result in a list [1 3 5]')
    parser.add_argument('--wild_range', '-nr', type=int, nargs='+',
                        help='used with sub_folder (wild) and specified in pairs e.g. 1 4 8 9 would result in a list [1 2 3 4 8 9]')
    parser.add_argument('--group_name', '-gn', nargs='+',
                        help='specifies the name of the subfolders.. if no name is specified or not enough names the run name in the data will be used')
    parser.add_argument('--remove_NMAUD', '-rt', default=True,
                        help='specifies whether to remove non-Maud files when performing the copy')
    if argsin==[]:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argsin.split(' '))

    return args

def copy_and_overwrite(from_path, to_path):
    for i in range(0,len(from_path)):
        if os.path.exists(to_path[i]):
            shutil.rmtree(to_path[i])
        shutil.copytree(from_path[i], to_path[i])

def group_files_by_dataset(root,files):
    udataset=[]
    for f in files:
        tmp=f.split('.')
        if tmp[-1] in '.tiff':
            tmp=tmp[-3]
                        
            dataset=tmp.split('-')[-1]
            
            data_dir = os.path.join(root, dataset)
            data_from = os.path.join(root,f)
            data_to = os.path.join(data_dir,f)
            
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            shutil.move(data_from,data_to)
            #print(dataset)
            udataset.append(dataset) if dataset not in udataset else udataset
    return udataset

def rename_datasets(root,udatasets,group_name):
    udatasets=sorted(udatasets)
    if group_name!=None:
        if len(udatasets) == len(group_name):
            for i,udataset in enumerate(udatasets):
                data_dir_from = os.path.join(root, udataset)
                data_dir_to = os.path.join(root, group_name[i])
                os.rename(data_dir_from,data_dir_to)
    else:
        for i,udataset in enumerate(udatasets):
            data_dir_from = os.path.join(root, udataset)
            data_dir_to = os.path.join(root, str(i))
            os.rename(data_dir_from,data_dir_to)

def build_paths(args):
            
    #Get wild cases if any and combine range and wild
    wild=[]
    if args.wild!=None:
        for i in args.wild:
            wild.append(i)
            
    if args.wild_range!=None:
        for pair in range(0,len(args.wild_range),2):
            tmp_id=range(args.wild_range[pair],args.wild_range[pair+1]+1)
            for i in tmp_id:
                wild.append(i)
                
    setattr(args, 'wild', wild)
    
    #build a list of for copies
    if wild!=[]:
        tmp_raw=[]
        tmp_out=[]
        #tmp_ofile=[]
        argattr_raw=args.data_dir_in
        argattr_out=args.data_dir_out
        #argattr_ofile=args.ofile
        for i in wild: 
            tmp_raw.append(argattr_raw.replace('(wild)',str(i)))
            tmp_out.append(argattr_out.replace('(wild)',str(i)))
            #if group_name!=None:
            #    for group in group_name:
            #        tmp_ofile.append(os.path.join(argattr_out.replace('(wild)',str(i)),argattr_ofile))
        setattr(args, 'data_dir_in', tmp_raw)
        setattr(args, 'data_dir_out', tmp_out)
        #setattr(args, 'ofile', tmp_ofile)
        
    if not isinstance(args.data_dir_in,list):
        setattr(args, 'data_dir_in', [args.data_dir_in])
        
    if not isinstance(args.data_dir_out,list):
        setattr(args, 'data_dir_out', [args.data_dir_out])
    
    #if not isinstance(args.ofile,list):
    #    setattr(args, 'ofile', [args.ofile])  
        
    return args

def main(argsin):
    #Get arguments from user
    args=get_arguments(argsin)
    args=build_paths(args)

    #Copy folders of interest
    copy_and_overwrite(args.data_dir_in,args.data_dir_out)
    # for ofile in args.ofile:
    #    shutil.copyfile(args.ifile,ofile)
        
    for out in args.data_dir_out:
        for root, dirs, files in os.walk(out, topdown=False):
            #print(root)
            #print(dirs)
            #print(files)
            udataset=group_files_by_dataset(root,files)
            rename_datasets(root,udataset,args.group_name)
            
            if args.remove_NMAUD:
                for f in files:
                    if '.tiff' not in f: 
                        os.remove(os.path.join(root, f))
    for out in args.data_dir_out:
        for root, dirs, files in os.walk(out, topdown=False):
            if not dirs==[]:
                for d in dirs:
                   shutil.copyfile(args.ifile,os.path.join(root,d,args.ofile))
    
    #     if 'run' in root:
    #         #Our run data has three digits..
    #         if int(root[-3:]) >= int(startrun) and int(root[-3:]) <= int(endrun):
    #             print(root)
    #             udataset = group_files_by_dataset(root,files)
    #             rename_datasets(udataset)
    #         else:
    #             shutil.rmtree(root)
    #     elif root != reffiledir:
    #         shutil.rmtree(root)

if __name__ == '__main__':
    main([])
