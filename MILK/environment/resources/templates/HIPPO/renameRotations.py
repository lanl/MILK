#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 21:45:11 2021

@author: danielsavage
"""

def read_file(ifile):
    with open(ifile) as f:
        lines = f.readlines()
    return lines

def write_file(lines,ofile):
    with open(ofile, 'w') as f:
        f.writelines("%s\n" % line.strip() for line in lines)

if __name__ == '__main__':

    for i in range(1,8):
        inoutfname=str(i)+'_rotations.par'
        
        #read template file
        lines = read_file(inoutfname)
        
        #Replace the omega 0.0, omega 67.5, etc... names
        for ind in range(0,len(lines)):
            line=lines[ind]
            if ' omega ' in line: 
                endstr=line.split(' omega ')[-1]
                line=line.replace(' omega '+endstr[0:3],' rotation '+endstr[0])
                lines[ind]=line  
            elif '../../../../../../Projects/MAUD_Batch_Language/Steel/CastSteel_' in line: 
                line=line.replace('../../../../../../Projects/MAUD_Batch_Language/Steel/CastSteel_','')
                lines[ind]=line  
            elif 'Z1221/raw/' in line: 
                line=line.replace('Z1221/raw/','')
                lines[ind]=line      
                
                
        #Write the parameter file to the directory
        write_file(lines,inoutfname)