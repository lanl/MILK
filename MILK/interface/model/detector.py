#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 16:35:10 2021

@author: danielsavage
"""

import argparse
import os

def read_par(ifile):
    with open(ifile) as f:
        lines = f.readlines()
    return lines

def write_par(lines,ofile):
    with open(ofile, 'w') as f:
        f.writelines("%s\n" % line.strip() for line in lines)
        
def rename_detector(lines, name):
    """Rename the detector object using the passed in naming convention and keeping the base detector name."""
    lines[0] = f"{lines[0]}_{name}"
    lines[-1] = f"{lines[-1]}_{name}"
    return lines

def search_list(lines):
    """Find the start and end of each detector object in MAUD parameter file.

    Args:
        lines (list of strings): Parameter file from MAUD read into list of strings.
    """
    index=[]
    sobj_cur=[]
    is_detector = False

    for i,line in enumerate(lines): 
        #keep track of the subordinate objects        
        if 'subordinateObject' in line:
            if 'end' in line:
                sobj_cur.pop()
                if len(sobj_cur)==0:
                    if is_detector:
                        #Store end of detector and reset detector flag
                        index[-1].append(i)
                        is_detector=False
                    else:
                        #Not a detector so don't consider
                        index.pop()
                    
            else:
                sobj_cur.append(line.partition('subordinateObject')[2])
                if len(sobj_cur)==1:
                    #First level of detector (maybe), store, will pop if no detector attributes found
                    index.append([i])

                
        else:
            if '_pd_meas_dataset_id' in line:
                is_detector=True
                index[-1].append(i)
    
    return index

    

def get_arguments(argsin):
    #Parse user arguments
    welcome = "This is an interface for duplicating detectors present in the MAUD file (e.g. for synchrotron texture."
    
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--work_dir', '-d', 
                        help='Relative path to directory to apply modifications to')
    parser.add_argument('--ifile', '-i', required=True, 
                        help='par file to which the texture information is added')
    parser.add_argument('--ofile', '-o',
                        help='A .par file name for saving')
    parser.add_argument('--postfix', '-p', nargs='+', required=True,
                        help='The name of detectors')
    parser.add_argument('--key', '-k',
                        help='Currently dumby')
    parser.add_argument('--sobj', '-s', nargs='+',action='append',
                        help='Currently dumby')
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

def setup_detectors(lines,indexs,postfix):
    """Repeat detector object len(postfix) times and append postfix to name

    Args:
        lines (list of strings): Parameter file from MAUD read into list of strings.
        indexs (list(list(int))): Starting and ending index in lines of each detector
        postfix (list(str)): Postfix to uniquely label each detector in the parameter file.

    Returns:
        list(str): list of full detector names.
    """

    #To not messup the indexing proceed from the end of the file
    detector_names=[]

    #Add first part of the parameter file
    lines_out = lines[:indexs[0][0]]
    for i,index in enumerate(indexs):
        for fix in postfix:
            tmp = lines[index[0]:index[2]+1]
            name = tmp[0].split("#subordinateObject_")[1].strip()
            detector_names.append(f"{name}_{fix}")
            tmp[0]=f"#subordinateObject_{detector_names[-1]}\n"
            tmp[index[1]-index[0]]=f"_pd_meas_dataset_id '{detector_names[-1]}'\n"
            tmp[-1]=f"#end_subordinateObject_{detector_names[-1]}\n"
            lines_out+=tmp

    #Add last part of the parameter file
    lines_out += lines[indexs[-1][2]+1:]

    return lines_out,detector_names

def main(argsin):
    #Get arguments from user
    args=get_arguments(argsin)
    
    #Main loop through files to edit
    for ind in range(0,len(args.ifile)):
        #read in the lines
        lines = read_par(args.ifile[ind])
                       
        #find the detector object indexes
        index=search_list(lines)
        
        lines,detector_names=setup_detectors(lines,index,args.postfix)
        
        #write back the par
        write_par(lines,args.ofile[ind])  

    return detector_names
if __name__ == '__main__':
    main([])
       
