#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 09:20:24 2021

@author: danielsavage
"""

import argparse
import os
import sys

def resource_file_path(filename):
    for d in sys.path:
        filepath = os.path.join(d, filename)
        if os.path.isfile(filepath):
            return filepath
    return None

def read_par(ifile):
    with open(ifile) as f:
        lines = f.readlines()
    return lines

def write_par(lines,ofile):
    with open(ofile, 'w') as f:
        f.writelines("%s\n" % line.strip() for line in lines)
        
def search_list(lines):
    index=[]
    sobj=[]
    sobj_cur=[]
    inphases=False
    
    for i in range(0,len(lines)): 
        line=lines[i]
               
        #keep track of the subordinate objects        
        if 'subordinateObject' in line:
            if 'end' in line:
                sobj_cur.pop()
            else:
                sobj_cur.append(line.partition('subordinateObject')[2])
                    
        if '_pd_phase_name' in line:
            inphases=True
        
        if inphases:
            if '#subordinateObject_Isotropic' in line or \
            '#subordinateObject_Anisotropic no rules' in line:
                index.append(i)
                sobj.append(sobj_cur[:])
            elif '#end_subordinateObject_Isotropic' in line or \
            '#end_subordinateObject_Anisotropic no rules' in line:
                index.append(i)
                sobj.append(sobj_cur[:])

    return [index,sobj]

def get_arguments(argsin):
    #Parse user arguments
    welcome = "This is an interface for setting the size-strain model of a phase(s)"
    
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--work_dir', '-d', 
                        help='Relative path to directory to apply modifications to')
    parser.add_argument('--ifile', '-i', required=True, 
                        help='par file to which the texture information is added')
    parser.add_argument('--ofile', '-o',
                        help='A .par file name for saving')
    parser.add_argument('--key', '-k',required=True,
                        help='The size-strain model to employ (options: Isotropic, Anisotropic)')
    parser.add_argument('--sobj', '-s', nargs='+',action='append',required=True,
                        help='Subordinate object string limits application of size-strain model to a sub section / phase of the .par files')
    parser.add_argument('--run_dir', '-dir',
                        help='Base directory from which sub folders are defined and par files are searched for')
    parser.add_argument('--sub_dir', '-sd',default='',
                        help='folders to run job in relative to run_directory /e.g. /run(runid)/preshock where (runid) is replaced by the wild and/or wild_range combined lists. wild need not be used')
    parser.add_argument('--wild', '-n', type=int, nargs='+',
                        help='used with sub_folder (wild) e.g. 1 3 5 would result in a list [1 3 5]')
    parser.add_argument('--wild_range', '-nr', type=int, nargs='+',
                        help='used with sub_folder (wild) and specified in pairs e.g. 1 4 8 9 would result in a list [1 2 3 4 8 9]')
    
    if argsin==[]:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argsin.split(' '))

    #Set the working directory
    if args.work_dir==None:
        args.work_dir = os.getcwd()

    #Get wild cases if any and combine range and wild
    wilds=[]
    if args.wild!=None:
        for i in args.wild:
            wilds.append(i)
            
    if args.wild_range!=None:
        for pair in range(0,len(args.wild_range),2):
            tmp_id=range(args.wild_range[pair],args.wild_range[pair+1]+1)
            for i in tmp_id:
                wilds.append(i)            
    wilds=list(set(wilds))

    #Build input file paths
    ifile=[]
    tmp = os.path.join(args.work_dir,args.run_dir,args.sub_dir,args.ifile)        
    for wild in wilds:
        ifile.append(tmp.replace('(wild)',str(wild).zfill(3)))          
    args.ifile=ifile

    #Generate the output file names
    if args.ofile==None:
        args.ofile = args.ifile
    else:
        ofile=[]
        for file in args.ifile:
            ofile.append(os.path.join(os.path.dirname(file),args.ofile) )
        args.ofile=ofile 
    
    return args

def insert_tex(lines,index,args):

    if args.key=='Isotropic':
        fname='IsotropicSizeStrain.txt'
    elif args.key=='Anisotropic':
        fname='AnisotropicSizeStrain.txt'
    else:
        raise NameError('SizeStrain not initialized correctly')
    
    fname=resource_file_path(fname)    
    assert fname!=None, 'Unable to find the support files for size-strain models' 
    
    lines_texModel = read_par(fname)

    #To not messup the indexing proceed from the end of the file
    for i in reversed(range(0,len(index),2)):
        for line in reversed(lines_texModel):
            lines.insert(index[i+1]+1,line)

        #Remove the old section
        for j in reversed(range(index[i],index[i+1]+1)):
            lines.pop(j)

    return lines

def main(argsin):
    #Get arguments from user
    args=get_arguments(argsin)
    
    #Main loop through files to edit
    for ind in range(0,len(args.ifile)):
        #read in the lines
        lines = read_par(args.ifile[ind])
                       
        tmp=search_list(lines)
        index=tmp[0]
        sobj_index=tmp[1]

                
        #Filter keyword by subordinate object
        if args.sobj[0][0] != None and args.sobj[0][0] != 'None':
            indextmp=[]
            for j in range(0,len(index)): 
                sobjs=''.join(sobj_index[j])
                if all(x in sobjs for x in args.sobj[0]):
                    indextmp.append(index[j])
            index=indextmp
        
        
        lines=insert_tex(lines,index,args)
        
        #write back the par
        write_par(lines,args.ofile[ind])    

if __name__ == '__main__':
    main([])
       