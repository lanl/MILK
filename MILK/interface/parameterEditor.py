#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 15:54:04 2020

@author: danielsavage
"""
import argparse
import os
from .model import (texture, sizeStrain,detector)
from pathlib import Path
import shutil
import sys
class arguments:
    def __init__(self):
        self.work_dir = None
        self.run_dirs = None
        self.wild = None
        self.wild_range = None
        self.key1 = None
        self.key2 = None
        self.ifile = None
        self.ofile = None
        self.task = None
        self.sobj1 = None
        self.sobj2 = None
        self.nsobj1 = None
        self.nsobj2 = None
        self.value = None
        self.loopid = None
        self.args = None
        self.verbose = None
        self.lines = None
        self.max_search_hits = None
        self.reverse_search = None
        self.zfill = None
        
    def parseConfig(self, config, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None, verbose=None,zfill=3):

        if work_dir == None:
            if config["folders"]["work_dir"] == '':
                self.work_dir = os.getcwd()
            else:
                self.work_dir = config["folders"]["work_dir"]
        else:
            self.work_dir = work_dir

        if ifile == None:
            self.ifile = config["ins"]["riet_analysis_file"]
        else:
            self.ifile = ifile

        if ofile == None:
            self.ofile = config["ins"]["riet_analysis_fileToSave"]
        else:
            self.ofile = ofile

        if run_dirs == None:
            self.run_dirs = config["folders"]["run_dirs"]
        else:
            self.run_dirs = run_dirs


        if wild == None:
            self.wild = config["folders"]["wild"]
        else:
            self.wild = wild

        if wild_range == None:
            self.wild_range = config["folders"]["wild_range"]
        else:
            self.wild_range = wild_range

        if verbose == None:
            self.verbose = config["ins"]["verbose"]
        else:
            self.verbose = verbose

        if "zfill" in config["folders"].keys():
            self.zfill = config["folders"]["zfill"] if config["folders"]["zfill"] is not None else zfill
        else:
            self.zfill = zfill

        #Purge wild_range
        wilds = self.wild
        if self.wild_range!=[[]]:
            for wild_range in self.wild_range:
                wilds+=list(range(wild_range[0],wild_range[1]+1))
        self.wild = list(set(wilds))
        self.wild_range = [[]]

    def parse_arguments(self):
        args = ''
        if self.task != None:
            args = args+'--task '+self.task+' '
        if self.key1 != None:
            args = args+'--key '+self.key1+' '
        if self.key2 != None:
            args = args+'--key '+self.key2+' '
        if self.sobj1 != None:
            args = args+'--sobj '+self.sobj1+' '
        if self.sobj2 != None:
            args = args+'--sobj '+self.sobj2+' '
        if self.nsobj1 != None:
            args = args+'--nsobj '+self.nsobj1+' '
        if self.nsobj2 != None:
            args = args+'--nsobj '+self.nsobj2+' '
        if self.value != None:
            args = args+'--value '+self.value+' '
        if self.loopid != None:
            args = args+'--loopid '+self.loopid+' '
        if self.ifile != None:
            args = args+'--ifile '+self.ifile+' '
        if self.ofile != None:
            args = args+'--ofile '+self.ofile+' '
        if self.work_dir != None:
            args = args+'--work_dir '+self.work_dir+' '
        if self.run_dirs != None:
            args = args+'--run_dir '+self.run_dirs+' '
        if self.wild != None and self.wild != []:
            args = args+'--wild '
            for wild in self.wild:
                args = args+str(wild)+' '
        if self.wild_range != None and self.wild_range != [[]]:
            args = args+'--wild_range '
            for wild_range in self.wild_range:
                args = args+str(wild_range[0])+' '+str(wild_range[1])+' '
        if self.verbose != None:
            args = args+'--verbose '+str(self.verbose)+' '
        if self.reverse_search != None:
            args = args+'--reverse_search '+str(self.reverse_search)+' '
        if self.max_search_hits != None:
            args = args+'--max_search_hits '+str(self.max_search_hits)+' '

        # trim at the end
        self.args = args[0:-1]

    def parse_arguments_model(self):
        args = ''

        if self.sobj1 != None:
            args = args+'--sobj '+self.sobj1+' '
        else:
            args = args+'--sobj None'+' '
        if self.key1 != None:
            args = args+'--key '+self.key1+' '
        if self.ifile != None:
            args = args+'--ifile '+self.ifile+' '
        if self.ofile != None:
            args = args+'--ofile '+self.ofile+' '
        if self.work_dir != None:
            args = args+'--work_dir '+self.work_dir+' '
        if self.run_dirs != None:
            args = args+'--run_dir '+self.run_dirs+' '
        if self.wild != None and self.wild != []:
            args = args+'--wild '
            for wild in self.wild:
                args = args+str(wild)+' '
        if self.wild_range != None and self.wild_range != [[]]:
            args = args+'--wild_range '
            for wild_range in self.wild_range:
                args = args+str(wild_range[0])+' '+str(wild_range[1])+' '
        if self.postfix != None:
            args = args + '--postfix '
            for postfix in self.postfix:
                args+=f"{postfix} "


        # trim at the end
        self.args = args[0:-1]


class editor(arguments):
    def __init__(self):
        super().__init__()

    def read_par(self):
        file = Path(self.ifile)
        assert file.is_file(), f"Parameter file <{file}> is not found on the absolute or relative path of the file"
        with open(self.ifile) as f:
            self.lines = f.readlines()

    def write_par(self):
        assert self.lines is not None, 'trying to write uninitialized lines'
        with open(self.ofile, 'w') as f:
            f.writelines("%s\n" % line.strip() for line in self.lines)

    def free(self, key, loopid=None, sobj=None, nsobj=None, run=True, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None,use_stored_par=False):
        '''
        free parameters in .par file
        Required Inputs: 
            keys     (str): Background, Intensity,ODFRefine,MicroStrain,CrystSize, DetPosX, DetPosY, DetPosDist, Biso, or userdefined (e.g. _riet_par_spec_displac_x)

        Optional inputs:   
            loopid   (str): a zero based integer specifying a parameter location in a loop variable. By default all loop values are changed
            sobj     (str): one or more subordinate objects to include in the scope of operation
            nsobj    (str): one or more subordinate objects to exclude in the scope of operation
            run     (bool): specifies whether to apply changes to parameter files
            ifile    (str): input parameter file 
            dir      (str): working work_dir

        Outputs: 
            Updates editor arguments and applies changes to parameter files if run=True(default)
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if use_stored_par:
            if self.lines is None:
                self.read_par()
            lines = self.lines
        else:
            lines = None
        self.key1 = key
        self.key2 = None
        self.task = 'free_par'
        self.sobj1 = sobj
        self.sobj2 = None
        self.nsobj1 = nsobj
        self.nsobj2 = None
        self.value = None
        self.loopid = loopid

        # combine the arguments and run if applicable
        self.parse_arguments()
        if run:
            self.ofile = main(self.args,lines,not use_stored_par)

        # Prevent reinitialization
        self.ifile = self.ofile

    def fix(self, key, loopid=None, sobj=None, nsobj=None, run=True, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None,use_stored_par=False):
        '''
        fix parameters in .par file
        Required Inputs: 
            keys     (str): Background, Intensity,ODFRefine,MicroStrain,CrystSize, DetPosX, DetPosY, DetPosDist, Biso, or userdefined (e.g. _riet_par_spec_displac_x)

        Optional inputs: 
            loopid   (str): a zero based integer specifying a parameter location in a loop variable. By default all loop values are changed
            sobj     (str): one or more subordinate objects to include in the scope of operation
            nsobj    (str): one or more subordinate objects to exclude in the scope of operation
            run     (bool): specifies whether to apply changes to parameter files
            ifile    (str): input parameter file 
            dir      (str): working work_dir

        Outputs: 
            Updates editor arguments and applies changes to parameter files if run=True(default)
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if use_stored_par:
            if self.lines is None:
                self.read_par()
            lines = self.lines
        else:
            lines = None
        self.key1 = key
        self.key2 = None
        self.task = 'fix_par'
        self.sobj1 = sobj
        self.sobj2 = None
        self.nsobj1 = nsobj
        self.nsobj2 = None
        self.value = None
        self.loopid = loopid

        # combine the arguments and run if applicable
        self.parse_arguments()
        if run:
            self.ofile = main(self.args,lines,not use_stored_par)

        # Prevent reinitialization
        self.ifile = self.ofile

    def add_SF(self, key, loopid=None, sobj=None, nsobj=None, run=True, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None,use_stored_par=False):
        '''
        add standard function component in .par file
        Required Inputs: 
            keys     (str): spherical, fiber
        Optional inputs:
            sobj     (str): one or more subordinate objects to include in the scope of operation
            nsobj    (str): one or more subordinate objects to exclude in the scope of operation
            run     (bool): specifies whether to apply changes to parameter files
            ifile    (str): input parameter file 
            dir      (str): working work_dir

        Outputs: 
            Updates editor arguments and applies changes to parameter files if run=True(default)
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if use_stored_par:
            if self.lines is None:
                self.read_par()
            lines = self.lines
        else:
            lines = None

        if loopid is None:
            loopid=1
        if key == "spherical":
            self.task = 'add_sf_spherical'
        elif key == "fiber":
            self.task = 'add_sf_fiber'
        else:
            raise NameError('Specify a valid key: spherical or fiber')

        self.key1 = "SF"
        self.key2 = None
        self.sobj1 = sobj
        self.sobj2 = None
        self.nsobj1 = nsobj
        self.nsobj2 = None
        self.value = None
        self.loopid = loopid

        # combine the arguments and run if applicable
        self.parse_arguments()
        if run:
            self.ofile = main(self.args,lines,not use_stored_par)

        # Prevent reinitialization
        self.ifile = self.ofile

    def set_val(self, key, value, loopid=None, sobj=None, nsobj=None, run=True, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None,use_stored_par=False):
        '''
        set parameter to a value in .par file
        Required Inputs: 
            keys     (str): Background, Intensity,ODFRefine,MicroStrain,CrystSize, DetPosX, DetPosY, DetPosDist, Biso, or userdefined (e.g. _riet_par_spec_displac_x)
            value    (str): A value to set
        Optional inputs:
            loopid   (str): a zero based integer specifying a parameter location in a loop variable. By default all loop values are changed
            sobj     (str): one or more subordinate objects to include in the scope of operation
            nsobj    (str): one or more subordinate objects to exclude in the scope of operation
            run     (bool): specifies whether to apply changes to parameter files
            ifile    (str): input parameter file 
            dir      (str): working work_dir

        Outputs: 
            Updates editor arguments and applies changes to parameter files if run=True(default)
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if use_stored_par:
            if self.lines is None:
                self.read_par()
            lines = self.lines
        else:
            lines = None
        if ('e-' in value or 'E-' in value):
            precision = int(value.split('-')[-1])
            value = f'{float(value):.{precision}f}'

        self.key1 = key
        self.key2 = None
        self.task = 'set_par'
        self.sobj1 = sobj
        self.sobj2 = None
        self.nsobj1 = nsobj
        self.nsobj2 = None
        self.value = value
        self.loopid = loopid

        # combine the arguments and run if applicable
        self.parse_arguments()
        if run:
            self.ofile = main(self.args,lines,not use_stored_par)

        # Prevent reinitialization
        self.ifile = self.ofile


    def get_key(self, key, sobj=None, nsobj=None, run=True, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None,use_stored_par=False):
        '''
        get the key value and subordinate information.
        Required Inputs: 
        Optional inputs:
            sobj     (str): one or more subordinate objects to include in the scope of operation
            nsobj    (str): one or more subordinate objects to exclude in the scope of operation
            run     (bool): specifies whether to apply changes to parameter files
            ifile    (str): input parameter file 
            dir      (str): working work_dir

        Outputs: 
            Updates editor arguments and populates editor.value
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if use_stored_par:
            if self.lines is None:
                self.read_par()
            lines = self.lines
        else:
            lines = None
        self.key1 = key
        self.key2 = None
        self.task = 'get_key'
        self.sobj1 = sobj
        self.sobj2 = None
        self.nsobj1 = nsobj
        self.nsobj2 = None
        self.value = None
        self.loopid = None

        # combine the arguments and run if applicable
        self.parse_arguments()
        if run:
            self.value = main(self.args,lines,False)

    def get_phases(self, sobj=None, nsobj=None, run=True, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None,use_stored_par=False):
        '''
        get the phase names in .par file
        Required Inputs: 
        Optional inputs:
            sobj     (str): one or more subordinate objects to include in the scope of operation
            nsobj    (str): one or more subordinate objects to exclude in the scope of operation
            run     (bool): specifies whether to apply changes to parameter files
            ifile    (str): input parameter file 
            dir      (str): working work_dir

        Outputs: 
            Updates editor arguments and populates editor.value
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if use_stored_par:
            if self.lines is None:
                self.read_par()
            lines = self.lines
        else:
            lines = None
        self.key1 = '_pd_phase_name'
        self.key2 = None
        self.task = 'get_phases'
        self.sobj1 = sobj
        self.sobj2 = None
        self.nsobj1 = nsobj
        self.nsobj2 = None
        self.value = None
        self.loopid = None

        # combine the arguments and run if applicable
        self.parse_arguments()
        if run:
            self.value = main(self.args,lines,False)

    def get_val(self, key, loopid=None, sobj=None, nsobj=None, run=True, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None,use_stored_par=False):
        '''
        get parameter value in .par file
        Required Inputs: 
            keys     (str): Background, Intensity,ODFRefine,MicroStrain,CrystSize, DetPosX, DetPosY, DetPosDist, Biso, or userdefined (e.g. _riet_par_spec_displac_x)
        Optional inputs:
            loopid   (str): a zero based integer specifying a parameter location in a loop variable. By default all loop values are changed
            sobj     (str): one or more subordinate objects to include in the scope of operation
            nsobj    (str): one or more subordinate objects to exclude in the scope of operation
            run     (bool): specifies whether to apply changes to parameter files
            ifile    (str): input parameter file 
            dir      (str): working work_dir

        Outputs: 
            Updates editor arguments and applies changes to parameter files if run=True(default)
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if use_stored_par:
            if self.lines is None:
                self.read_par()
            lines = self.lines
        else:
            lines = None

        self.key1 = key
        self.key2 = None
        self.task = 'get_val'
        self.sobj1 = sobj
        self.sobj2 = None
        self.nsobj1 = nsobj
        self.nsobj2 = None
        self.value = None
        self.loopid = loopid

        # combine the arguments and run if applicable
        self.parse_arguments()

        if run:
            self.value = main(self.args,lines,False)

    def get_err(self, key, loopid=None, sobj=None, nsobj=None, run=True, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None,use_stored_par=False):
        '''
        get parameter value err in .par file
        Required Inputs: 
            keys     (str): Background, Intensity,ODFRefine,MicroStrain,CrystSize, DetPosX, DetPosY, DetPosDist, Biso, or userdefined (e.g. _riet_par_spec_displac_x)
        Optional inputs:
            loopid   (str): a zero based integer specifying a parameter location in a loop variable. By default all loop values are changed
            sobj     (str): one or more subordinate objects to include in the scope of operation
            nsobj    (str): one or more subordinate objects to exclude in the scope of operation
            run     (bool): specifies whether to apply changes to parameter files
            ifile    (str): input parameter file 
            dir      (str): working work_dir

        Outputs: 
            Updates editor arguments and applies changes to parameter files if run=True(default)
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if use_stored_par:
            if self.lines is None:
                self.read_par()
            lines = self.lines
        else:
            lines = None
        
        self.key1 = key
        self.key2 = None
        self.task = 'get_err'
        self.sobj1 = sobj
        self.sobj2 = None
        self.nsobj1 = nsobj
        self.nsobj2 = None
        self.value = None
        self.loopid = loopid

        # combine the arguments and run if applicable
        self.parse_arguments()
        if run:
            self.value = main(self.args,lines,False)

    def fix_all(self, sobj=None, nsobj=None, run=True, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None,use_stored_par=False):
        '''
        fix all parameters in .par file
        Optional inputs: 
            sobj     (str): one or more subordinate objects to include in the scope of operation
            nsobj    (str): one or more subordinate objects to exclude in the scope of operation
            run     (bool): specifies whether to apply changes to parameter files
            ifile    (str): input parameter file 
            dir      (str): working work_dir

        Outputs: 
            Updates editor arguments and applies changes to parameter files if run=True(default)
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if use_stored_par:
            if self.lines is None:
                self.read_par()
            lines = self.lines
        else:
            lines = None
        self.key1 = 'blah'
        self.key2 = None
        self.task = 'fix_all'
        self.sobj1 = sobj
        self.sobj2 = None
        self.nsobj1 = nsobj
        self.nsobj2 = None
        self.value = None
        self.loopid = None

        # combine the arguments and run if applicable
        self.parse_arguments()
        if run:
            self.ofile = main(self.args,lines,not use_stored_par)

        # Prevent reinitialization
        self.ifile = self.ofile

    def ref(self, key1, key2, value, loopid=None, sobj1='None', sobj2='None', nsobj1='None', nsobj2='None', run=True, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None,use_stored_par=False):
        '''
        set parameter to an equation with another parameter value in it
        Required Inputs: 
            key1     (str): Background, Intensity,ODFRefine,MicroStrain,CrystSize, DetPosX, DetPosY, DetPosDist, Biso, or userdefined (e.g. _riet_par_spec_displac_x)
            key2(ref)(str): Background, Intensity,ODFRefine,MicroStrain,CrystSize, DetPosX, DetPosY, DetPosDist, Biso, or userdefined (e.g. _riet_par_spec_displac_x)
            value    (str): A triplet of values (e.g. 1 2 10000 which gives 1 + 2*var at reference 10000) best to set to large unique value and let MAUD relabel
        Optional inputs:
            loopid   (str): a zero based integer specifying a parameter location in a loop variable. By default all loop values are changed
            sobj1    (str): one or more subordinate objects to include in the scope of operation
            sobj2    (str): one or more subordinate objects to include in the scope of operation
            nsobj1   (str): one or more subordinate objects to exclude in the scope of operation
            nsobj2   (str): one or more subordinate objects to exclude in the scope of operation
            run     (bool): specifies whether to apply changes to parameter files
            ifile    (str): input parameter file 
            dir      (str): working work_dir

        Outputs: 
            Updates editor arguments and applies changes to parameter files if run=True(default)
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if use_stored_par:
            if self.lines is None:
                self.read_par()
            lines = self.lines
        else:
            lines = None
        self.key1 = key1
        self.key2 = key2
        self.task = 'ref_par'
        self.sobj1 = sobj1
        self.sobj2 = sobj2
        self.nsobj1 = nsobj1
        self.nsobj2 = nsobj2
        self.value = value
        self.loopid = loopid

        # combine the arguments and run if applicable
        self.parse_arguments()
        if run:
            self.ofile = main(self.args,lines,not use_stored_par)

        # Prevent reinitialization
        self.ifile = self.ofile

    def un_ref(self):
        print('un_ref is currently unimplemented')
 
    def add_datafile_bk_par(self, sobj=None, nsobj=None, run=True, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None,use_stored_par=False):
        '''
        add individual datafile background parameter.
        Optional inputs: 
            sobj     (str): one or more subordinate objects to include in the scope of operation
            nsobj    (str): one or more subordinate objects to exclude in the scope of operation
            run     (bool): specifies whether to apply changes to parameter files
            ifile    (str): input parameter file 
            dir      (str): working work_dir

        Outputs: 
            Updates editor arguments and applies changes to parameter files if run=True(default)
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if use_stored_par:
            if self.lines is None:
                self.read_par()
            lines = self.lines
        else:
            lines = None
        self.key1 = 'Background'
        self.key2 = None
        self.task = 'add_datafile_bk_par'
        self.sobj1 = sobj
        self.sobj2 = None
        self.nsobj1 = nsobj
        self.nsobj2 = None
        self.value = None
        self.loopid = None

        # combine the arguments and run if applicable
        self.parse_arguments()
        if run:
            self.ofile = main(self.args,lines,not use_stored_par)

        # Prevent reinitialization
        self.ifile = self.ofile

    def add_loop_par(self, key, sobj=None, nsobj=None, run=True, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None,use_stored_par=False):
        '''
        add parameters to a loop variable. Should probably only be used with background to my knowledge
        Required Inputs: 
            keys     (str): Background
        Optional inputs: 
            sobj     (str): one or more subordinate objects to include in the scope of operation
            nsobj    (str): one or more subordinate objects to exclude in the scope of operation
            run     (bool): specifies whether to apply changes to parameter files
            ifile    (str): input parameter file 
            dir      (str): working work_dir

        Outputs: 
            Updates editor arguments and applies changes to parameter files if run=True(default)
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if use_stored_par:
            if self.lines is None:
                self.read_par()
            lines = self.lines
        else:
            lines = None
        self.key1 = key
        self.key2 = None
        self.task = 'add_par'
        self.sobj1 = sobj
        self.sobj2 = None
        self.nsobj1 = nsobj
        self.nsobj2 = None
        self.value = None
        self.loopid = None

        # combine the arguments and run if applicable
        self.parse_arguments()
        if run:
            self.ofile = main(self.args,lines,not use_stored_par)

        # Prevent reinitialization
        self.ifile = self.ofile

    def rem_loop_par(self, key, sobj=None, nsobj=None, run=True, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None,use_stored_par=False):
        '''
        remove parameters in a loop variable. Should probably only be used with background
        Required Inputs: 
            keys     (str): Background
        Optional inputs: 
            sobj     (str): one or more subordinate objects to include in the scope of operation
            nsobj    (str): one or more subordinate objects to exclude in the scope of operation
            run     (bool): specifies whether to apply changes to parameter files
            ifile    (str): input parameter file 
            dir      (str): working work_dir

        Outputs: 
            Updates editor arguments and applies changes to parameter files if run=True(default)
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if use_stored_par:
            if self.lines is None:
                self.read_par()
            lines = self.lines
        else:
            lines = None
        self.key1 = key
        self.key2 = None
        self.task = 'rem_par'
        self.sobj1 = sobj
        self.sobj2 = None
        self.nsobj1 = nsobj
        self.nsobj2 = None
        self.value = None
        self.loopid = None

        # combine the arguments and run if applicable
        self.parse_arguments()
        if run:
            self.ofile = main(self.args,lines,not use_stored_par)

        # Prevent reinitialization
        self.ifile = self.ofile
    def run_copy_file(self,target,dest,work_dir=None, run_dirs=None, wild=None, wild_range=None):
        '''
        Copy files using the run folders path generation.
        Required Inputs: 
            target  (str): File you wish to copy relative to work and run directories
            dest    (str): Destination file you wish to make relative to work and run directories.

        Outputs: 
            Copies target to dest
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if run_dirs != None:
            self.run_dirs = run_dirs
        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range

        # Get wild cases if any and combine range and wild
        wilds = []
        if self.wild != None:
            for i in self.wild:
                wilds.append(i)

        if self.wild_range != None:
            for pair in self.wild_range:
                if pair !=[]:
                    tmp_id = range(pair[0], pair[1])               
                    for i in tmp_id:
                        wilds.append(i)
        wilds = list(set(wilds))

        infiles = Path(self.work_dir) / self.run_dirs / target
        outfiles = Path(self.work_dir) / self.run_dirs / dest
        if wilds==[] or '(wild)' not in str(infiles):
            if outfiles.exists():
                outfiles.unlink()
            shutil.copy(infiles,outfiles)
        else:
            for wild in wilds:
                infile = str(infiles).replace('(wild)', str(wild).zfill(self.zfill))
                outfile = str(outfiles).replace('(wild)', str(wild).zfill(self.zfill))
                if Path(outfile).exists():
                    Path(outfile).unlink()
                shutil.copy(infile,outfile)

    def load_archived_step(self, step_number: int, maudText=None, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None):
        '''
        Load a MILK archived step to the work directory and set editor and MAUDText parameters
        Required Inputs: 
            step_number (str): step_number

        Optional Inputs: 
            MaudText    (obj): MaudText object for step setting (default=None).
            ifile    (str): input parameter file 
            dir      (str): working work_dir
        Outputs: 
            Copies input par and editor arguments with references for the step
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if run_dirs != None:
            self.run_dirs = run_dirs
        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        # Get wild cases if any and combine range and wild
        wilds = []
        if self.wild != None:
            for i in self.wild:
                wilds.append(i)

        if self.wild_range != None:
            for pair in self.wild_range:
                if pair !=[]:
                    tmp_id = range(pair[0], pair[1])               
                    for i in tmp_id:
                        wilds.append(i)
        wilds = list(set(wilds))

        infiles = Path(self.work_dir) / self.run_dirs / f"step_{step_number}" / self.ifile
        outfiles = Path(self.work_dir) / self.run_dirs / self.ofile
        if wilds==[] or '(wild)' not in str(infiles):
            if outfiles.exists():
                outfiles.unlink()
            shutil.copy(infiles,outfiles)
        else:
            for wild in wilds:
                infile = str(infiles).replace('(wild)', str(wild).zfill(self.zfill))
                if ifile is None:
                    pars = list(Path(infile).parent.glob("*.par"))
                    if len(pars) >1: 
                        print(f"Warning: More than one .par file found in {Path(infile).parent}. Using {pars[0]}")
                    elif len(pars)==0:
                        raise FileNotFoundError(f"No .par file was found in {Path(infile).parent}")
                    infile = str(pars[0])
                outfile = str(outfiles).replace('(wild)', str(wild).zfill(self.zfill))
                if Path(outfile).exists():
                    Path(outfile).unlink()
                shutil.copy(infile,outfile)
        if maudText is not None:
            maudText.cur_step = step_number+1
            maudText.ifile=self.ofile
        self.ifile = self.ofile


    def reset_odf(self, sobj=None, nsobj=None, run=True, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None,use_stored_par=False):
        '''
        reset the ODF 

        Optional inputs: 
            sobj     (str): one or more subordinate objects to include in the scope of operation
            nsobj    (str): one or more subordinate objects to exclude in the scope of operation
            run     (bool): specifies whether to apply changes to parameter files
            ifile    (str): input parameter file 
            dir      (str): working work_dir

        Outputs: 
            Updates editor arguments and applies changes to parameter files if run=True(default)
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if use_stored_par:
            if self.lines is None:
                self.read_par()
            lines = self.lines
        else:
            lines = None
        self.key1 = 'ODFValues'
        self.key2 = None
        self.task = 'reset_odf'
        self.sobj1 = sobj
        self.sobj2 = None
        self.nsobj1 = nsobj
        self.nsobj2 = None
        self.value = None
        self.loopid = None

        # combine the arguments and run if applicable
        self.parse_arguments()
        if run:
            self.ofile = main(self.args,lines,not use_stored_par)

        # Prevent reinitialization
        self.ifile = self.ofile

    def track(self, key, loopid=None, sobj=None, nsobj=None, run=True, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None,use_stored_par=False):
        '''
        tracking a parameter outputs its value to the summary document after a refinement
        Required Inputs: 
            keys     (str): Background, Intensity,ODFRefine,MicroStrain,CrystSize, DetPosX, DetPosY, DetPosDist, Biso, or userdefined (e.g. _riet_par_spec_displac_x)
        Optional inputs:
            loopid   (str): a zero based integer specifying a parameter location in a loop variable. By default all loop values are changed
            sobj     (str): one or more subordinate objects to include in the scope of operation
            nsobj    (str): one or more subordinate objects to exclude in the scope of operation
            run     (bool): specifies whether to apply changes to parameter files
            ifile    (str): input parameter file 
            dir      (str): working work_dir

        Outputs: 
            Updates editor arguments and applies changes to parameter files if run=True(default)
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if use_stored_par:
            if self.lines is None:
                self.read_par()
            lines = self.lines
        else:
            lines = None
        self.key1 = key
        self.key2 = None
        self.task = 'track_par'
        self.sobj1 = sobj
        self.sobj2 = None
        self.nsobj1 = nsobj
        self.nsobj2 = None
        self.value = None
        self.loopid = loopid

        # combine the arguments and run if applicable
        self.parse_arguments()
        if run:
            self.ofile = main(self.args,lines,not use_stored_par)

        # Prevent reinitialization
        self.ifile = self.ofile

    def untrack(self, key, loopid=None, sobj=None, nsobj=None, run=True, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None,use_stored_par=False):
        '''
        untracking a parameter outputs stops its value from being printed in summary document after a refinement unless basic parameter
        Required Inputs: 
            keys     (str): Background, Intensity,ODFRefine,MicroStrain,CrystSize, DetPosX, DetPosY, DetPosDist, Biso, or userdefined (e.g. _riet_par_spec_displac_x)
        Optional inputs:
            loopid   (str): a zero based integer specifying a parameter location in a loop variable. By default all loop values are changed
            sobj     (str): one or more subordinate objects to include in the scope of operation
            nsobj    (str): one or more subordinate objects to exclude in the scope of operation
            run     (bool): specifies whether to apply changes to parameter files
            ifile    (str): input parameter file 
            dir      (str): working work_dir

        Outputs: 
            Updates editor arguments and applies changes to parameter files if run=True(default)
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if use_stored_par:
            if self.lines is None:
                self.read_par()
            lines = self.lines
        else:
            lines = None
        self.key1 = key
        self.key2 = None
        self.task = 'untrack_par'
        self.sobj1 = sobj
        self.sobj2 = None
        self.nsobj1 = nsobj
        self.nsobj2 = None
        self.value = None
        self.loopid = loopid

        # combine the arguments and run if applicable
        self.parse_arguments()
        if run:
            self.ofile = main(self.args,lines,not use_stored_par)

        # Prevent reinitialization
        self.ifile = self.ofile

    def untrack_all(self, sobj=None, nsobj=None, run=True, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None,use_stored_par=False):
        '''
        untracking all parameter outputs and stops there value from being printed in summary document after a refinement unless basic parameter
        Optional inputs:
            loopid   (str): a zero based integer specifying a parameter location in a loop variable. By default all loop values are changed
            sobj     (str): one or more subordinate objects to include in the scope of operation
            nsobj    (str): one or more subordinate objects to exclude in the scope of operation
            run     (bool): specifies whether to apply changes to parameter files
            ifile    (str): input parameter file 
            dir      (str): working work_dir

        Outputs: 
            Updates editor arguments and applies changes to parameter files if run=True(default)
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if use_stored_par:
            if self.lines is None:
                self.read_par()
            lines = self.lines
        else:
            lines = None
        self.key1 = None
        self.key2 = None
        self.task = 'untrack_all'
        self.sobj1 = sobj
        self.sobj2 = None
        self.nsobj1 = nsobj
        self.nsobj2 = None
        self.value = None
        self.loopid = None

        # combine the arguments and run if applicable
        self.parse_arguments()
        if run:
            self.ofile = main(self.args,lines,not use_stored_par)

        # Prevent reinitialization
        self.ifile = self.ofile


    def texture(self, key=None, sobj=None, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None, run=True):
        '''
              texture inserts a MAUD texture model into all phases or to particular phase using sobj
              key options: None, Arbitrary, EWIMV, SF

              Outputs: 
                  Updates editor arguments and applies changes to parameter files
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if key != None and key in 'None, Arbitrary, EWIMV, SF':
            self.key1 = key
        else:
            raise NameError('Specify a valid key: None, Arbitrary, EWIMV, SF')
        self.sobj1 = sobj
        self.postfix=None
        # combine the arguments and run if applicable
        self.parse_arguments_model()
        if run:
            self.ofile = texture.main(self.args)

        # Prevent reinitialization
        self.ifile = self.ofile

    def size_strain(self, key=None, sobj=None, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None, run=True):
        '''
              size_strain inserts a MAUD size-strain model into all phases or to particular phase using sobj
              key options: Isotropic, Anisotropic)

              Outputs: 
                  Updates editor arguments and applies changes to parameter files
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if key != None and key in 'Isotropic, Anisotropic':
            self.key1 = key
        else:
            raise NameError('Specify a valid key: Isotropic, Anisotropic)')
        self.sobj1 = sobj
        self.postfix=None

        # combine the arguments and run if applicable
        self.parse_arguments_model()
        if run:
            self.ofile = sizeStrain.main(self.args)

        # Prevent reinitialization
        self.ifile = self.ofile

    def detector(self, postfix=None, ifile=None, ofile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None, run=True):
        '''
              detector duplicates a MAUD detectors len(postfix) times and add postfix to each detector instance.

              Outputs: 
                  stores the detector_names for use elsewhere.
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if ifile != None:
            self.ifile = ifile
        if ofile != None:
            self.ofile = ofile
        if run_dirs != None:
            self.run_dirs = run_dirs

        if wild != None:
            self.wild = wild
        if wild_range != None:
            self.wild_range = wild_range
        if postfix != None:
            self.postfix = postfix
        else:
            raise NameError('Specify a list of postfix strings)')
        self.key=None
        self.sobj1=None

        # combine the arguments and run if applicable
        self.parse_arguments_model()
        if run:
            detector_names,self.ofile=detector.main(self.args)
        else:
            detector_names=[]

        # Prevent reinitialization
        self.ifile = self.ofile
        return detector_names

    def summary(self, ifile=None, work_dir=None, run_dirs=None, wild=None, wild_range=None):
        if ifile == None:
            ifile = self.ifile
        # Set the working work_dir
        if work_dir == None and self.work_dir != None:
            work_dir = self.work_dir
        elif work_dir == None:
            work_dir = os.getcwd()
        if run_dirs == None:
            run_dirs = self.run_dirs

        # Get wild cases if any and combine range and wild
        wilds = []
        if wild == None:
            wild = self.wild
        if wild_range == None:
            wild_range = self.wild_range

        wilds = []
        for i in wild:
            wilds.append(i)
        if wild_range !=[[]]:
            for pair in wild_range:
                tmp_id = range(pair[0], pair[1]+1)
                for i in tmp_id:
                    wilds.append(i)
        wilds = list(set(wilds))

        # Build input file paths
        ifiles = []
        tmp = os.path.join(work_dir, run_dirs, ifile)
        for wild in wilds:
            ifiles.append(tmp.replace('(wild)', str(wild).zfill(self.zfill)))

        # Main loop through files to edit
        for ind in range(0, len(ifiles)):
            # read in the lines
            lines = read_par(ifiles[ind])
            nfree = 0
            inloop = False
            d = dict()
            for ind2, line in enumerate(lines):
                if 'loop_' in line:
                    key = lines[ind2+1]
                    inloop = True
                if inloop and not bool(line.strip()):
                    inloop = False
                indstart = line.find('(')
                if indstart > -1 and '#min' in line:
                    nfree += 1
                    if not inloop:
                        key = line.split(' ')[0]
                    if key in d:
                        d[key] += 1
                    else:
                        d[key] = 1
            print('========================')
            print('in file: '+ifiles[ind])
            print(str(nfree)+' parameters are free')
            print('Number of free parameters per key')
            print('=================================')
            for key in d:
                print(key.strip()+': '+str(d[key]))
            print('')


def read_par(ifile):
    with open(ifile) as f:
        lines = f.readlines()
    return lines


def write_par(lines, ofile):
    with open(ofile, 'w') as f:
        f.writelines("%s\n" % line.strip() for line in lines)


def search_list_reverse(lines, keyword, d, max_hit=1e6):
    index = []
    isloop = []
    indloop = []
    endloop = []
    sobj = []
    sobj_cur = []

    hits = 1
    sobj_cur = ["test"]
    lines = list(reversed(lines))
    llines = len(lines)
    for i,line in enumerate(lines):
    
        # keep track of the subordinate objects
        if 'subordinateObject' in line:
            if 'end' not in line:
                sobj_cur.pop()
            else:
                sobj_cur.append(line.partition('subordinateObject')[2])

        if keyword in line:
            # handle loop variables (e.g. background polynomial)
            if 'loop_' not in lines[i+1]:
                index.append(llines-i-1)
                sobj.append(sobj_cur[:])
                isloop.append(False)
                endloop.append(False)
                indloop.append(-1)
            elif keyword != d['ODFValues']:
                ind = i-1
                line = lines[ind]
                indlooploc = 0
                while bool(line.strip()):
                    index.append(ind)
                    sobj.append(sobj_cur[:])
                    indloop.append(indlooploc)
                    isloop.append(True)
                    endloop.append(False)
                    ind = ind-1
                    indlooploc = indlooploc+1
                    line = lines[ind]
                endloop[-1] = True
            else:
                ind = i-1
                line = lines[ind]
                while '#end_custom_object_odf' not in line:
                    index.append(ind)
                    sobj.append(sobj_cur[:])
                    isloop.append(True)
                    endloop.append(False)
                    ind = ind-1
                    line = lines[ind]
                endloop[-1] = True
            
            hits+=1
            if hits>max_hit:
                return [index, sobj, isloop, indloop, endloop]

    return [index, sobj, isloop, indloop, endloop]

def search_list(lines, keyword, d,max_hit=1e6):
    index = []
    isloop = []
    indloop = []
    endloop = []
    sobj = []
    sobj_cur = []

    hits = 1
    for i,line in enumerate(lines):
    
        # keep track of the subordinate objects
        if 'subordinateObject' in line:
            if 'end' in line:
                sobj_cur.pop()
            else:
                sobj_cur.append(line.partition('subordinateObject')[2])

        if keyword in line:
            if keyword == d['ODFValues']:
                ind = i+1
                line = lines[ind]
                while '#end_custom_object_odf' not in line:
                    index.append(ind)
                    sobj.append(sobj_cur[:])
                    isloop.append(True)
                    endloop.append(False)
                    ind = ind+1
                    line = lines[ind]
                if endloop != [] and not endloop[-1]:
                    endloop[-1] = True
            elif keyword == d['SF']:
                index.append(i+7)
                sobj.append(sobj_cur[:])
                isloop.append(False)
                endloop.append(False)
                indloop.append(-1)
            # handle loop variables (e.g. background polynomial)
            elif 'loop_' not in lines[i-1]:
                index.append(i)
                sobj.append(sobj_cur[:])
                isloop.append(False)
                endloop.append(False)
                indloop.append(-1)
            else:
                #is loop
                ind = i+1
                line = lines[ind]
                indlooploc = 0
                # if not bool(line.strip()):
                #     index.append(ind)
                #     sobj.append(sobj_cur[:])
                #     indloop.append(indlooploc)
                #     isloop.append(True)
                #     endloop.append(True)
                while bool(line.strip()):
                    index.append(ind)
                    sobj.append(sobj_cur[:])
                    indloop.append(indlooploc)
                    isloop.append(True)
                    endloop.append(False)
                    ind = ind+1
                    indlooploc = indlooploc+1
                    line = lines[ind]

                endloop[-1] = True



            hits+=1
            if hits>max_hit:
                return [index, sobj, isloop, indloop, endloop]

    return [index, sobj, isloop, indloop, endloop]


def free_parameter(lines, index, isloop, indloop, loopid):
    nlineMod = 0
    for i in range(0, len(index)):
        ind = index[i]
        line = lines[ind].split()

        indstart = lines[ind].find('(')
        if indstart == -1:
            if isloop[i]:
                offset = 0
                if str(indloop[i]) == loopid or loopid == 'None':
                    nlineMod += 1
                    line[offset] = line[offset]+'(0.0)'
                    lines[ind] = " ".join(line)
            else:
                offset = 1
                nlineMod += 1
                line[offset] = line[offset]+'(0.0)'
                lines[ind] = " ".join(line)
    return lines, nlineMod


def set_par(lines, value, index, isloop, indloop, loopid):
    nlineMod = 0
    for i in range(0, len(index)):
        ind = index[i]
        line = lines[ind].split()

        # Get if it is a loop variable in which case the value is at index 0 else 1
        if isloop[i]:
            if str(indloop[i]) == loopid or loopid == 'None':
                nlineMod += 1
                offset = 0

                # If the variable is being refined, reset the refinement value
                indstart = lines[ind].find('(')
                if indstart == -1:
                    line[offset] = str(value[0])
                else:
                    # refining
                    line[offset] = str(value[0])+'(0.0)'

                lines[ind] = " ".join(line)

        else:
            nlineMod += 1
            offset = 1

            # If the variable is being refined, reset the refinement value
            indstart = lines[ind].find('(')
            if indstart == -1:
                line[offset] = str(value[0])
            else:
                # refining
                line[offset] = str(value[0])+'(0.0)'

            lines[ind] = " ".join(line)
    return lines, nlineMod


def get_val(lines, index, isloop, indloop, loopid):
    value = []
    for i, ind in enumerate(index):
        if isloop[i]:
            offset = 0
            if str(indloop[i]) == loopid or loopid == 'None':
                tmp = lines[ind].lstrip(' ')
                tmp = tmp.split(' ')[offset]
                value.append(tmp.split('(')[0])
        else:
            offset = 1
            tmp = lines[ind].lstrip(' ')
            tmp = tmp.split(' ')[offset]
            value.append(tmp.split('(')[0])

    return value

def get_phases(lines, index):
    value = []
    for i, ind in enumerate(index):
        tmp = lines[ind].replace("_pd_phase_name ","").replace("'","").strip()
        value.append(tmp)

    return value

def get_key_value(lines, index, isloop, indloop, loopid, sobj,keyword):
    key_value = []
    for i, ind in enumerate(index):
        value = get_val(lines, [ind], [isloop[i]], [indloop[i]], loopid)
        key_value.append({"key":keyword,"sobj": [s.replace("\n","") for s in sobj[i]],"value": value})

    return key_value

def get_err(lines, index, isloop, indloop, loopid):
    err = []
    for i, ind in enumerate(index):
        if isloop[i]:
            offset = 0
            if str(indloop[i]) == loopid or loopid == 'None':
                tmp = lines[ind].lstrip(' ')
                tmp = tmp.split(' ')[offset]
                if '(' in tmp:
                    err.append(tmp.split('(')[1].split(')')[0])
                else:
                    err.append('0.0')
        else:
            offset = 1
            tmp = lines[ind].lstrip(' ')
            tmp = tmp.split(' ')[offset]
            if '(' in tmp:
                err.append(tmp.split('(')[1].split(')')[0])
            else:
                err.append('0.0')

    return err


def fix_parameter(lines, index, isloop, indloop, loopid):
    nlineMod = 0
    for i in range(0, len(index)):
        ind = index[i]
        line = lines[ind]
        indstart = line.find('(')
        indend = line.find(')')
        if isloop[i]:
            if str(indloop[i]) == loopid or loopid == 'None':
                nlineMod += 1
                lines[ind] = line.replace(line[indstart:indend+1], "")
        else:
            nlineMod += 1
            lines[ind] = line.replace(line[indstart:indend+1], "")
        # imin = line.index('#min')
        # imax = line.index('#max')
        #lines[ind] = [j for i, j in enumerate(lines[ind]) if i not in range(indstart,indend+1)]
    return lines, nlineMod


def fix_all(lines):
    nlineMod = 0
    for ind in range(0, len(lines)):
        indstart = lines[ind].find('(')
        if indstart > -1 and '#min' in lines[ind]:
            nlineMod += 1
            tmp = fix_parameter([lines[ind]], [0], [False], [], [])[0]
            lines[ind] = tmp[0]

    return lines, nlineMod


def untrack_all(lines):
    nlineMod = 0
    for ind in range(0, len(lines)):
        if ' #autotrace' in lines[ind]:
            lines[ind] = lines[ind].replace(' #autotrace', '')
    return lines, nlineMod


def track_par(lines, index, isloop, indloop, loopid):
    nlineMod = 0
    for i in range(0, len(index)):
        ind = index[i]
        line = lines[ind].split()

        if '#autotrace' not in lines[ind]:
            if isloop[i]:
                offset = 0
                if str(indloop[i]) == loopid or loopid == 'None':
                    nlineMod += 1
                    line[offset] = line[offset]+' #autotrace'
                    lines[ind] = " ".join(line)
            else:
                nlineMod += 1
                offset = 1
                line[offset] = line[offset]+' #autotrace'
                lines[ind] = " ".join(line)
    return lines, nlineMod


def untrack_par(lines, index, isloop, indloop, loopid):
    nlineMod = 0
    for i in range(0, len(index)):
        ind = index[i]
        if ' #autotrace' in lines[ind]:
            nlineMod += 1
            lines[ind] = lines[ind].replace(' #autotrace', '')

    return lines, nlineMod


def ref_par(lines, index, value, isloop, indloop, loopid):
    nlineMod = 0
    # Add loop support here
    assert len(index) == 2, 'Both parts of the reference were not passed in.'
    assert len(
        index[1]) == 1, 'Your second argument specified multiple lines. Only one line can be referenced at a time!'
    for ind in index[1]:
        line = lines[ind].split()
        reference = '#ref'+str(value[2])
        isReference = False
        for word in line:
            if '#ref' in word:
                #print('Target reference already has a number. Using ' + word + ' instead of ' + reference)
                reference = word
                isReference = True
        if not isReference:
            nlineMod += 1
            line.append(reference)
            lines[ind] = " ".join(line)

    for i, ind in enumerate(index[0]):
        line = lines[ind].split()

        isEqualTo = False
        for j in range(len(line)):
            word = line[j]
            if '#equalTo' in word:

                isEqualTo = True
                line[j+1] = value[0]
                line[j+3] = value[1]
                line[j+5] = reference

        if not isEqualTo:
            line.append('#equalTo')
            line.append(value[0])  # equalTo 0.5 + 0 * #ref8
            line.append('+')
            line.append(value[1])
            line.append('*')
            line.append(reference)

        if isloop[0][i]:
            if str(indloop[0][i]) == loopid or loopid == 'None':
                nlineMod += 1
                lines[ind] = " ".join(line)
        else:
            nlineMod += 1
            lines[ind] = " ".join(line)

    return lines, nlineMod

def resource_file_path(filename):
    for d in sys.path:
        filepath = os.path.join(d, filename)
        if os.path.isfile(filepath):
            return filepath
    return None

def add_sf_component(lines,index,task,loopid):
    if task=="add_sf_spherical":
        filename = resource_file_path("SFSpherical.txt")
        component_lines = read_par(filename)
        component_lines[0] = f"#subordinateObject_ori{loopid}"
        component_lines[2] = f"_texture_spherical_component_id 'ori{loopid}'"
        component_lines[-2] = f"#end_subordinateObject_ori{loopid}"
    elif task=="add_sf_fiber":
        filename = resource_file_path("SFFiber.txt")
        component_lines = read_par(filename)
        component_lines[0] = f"#subordinateObject_fiber{loopid}"
        component_lines[2] = f"_texture_fiber_component_id 'fiber{loopid}'"
        component_lines[-2] = f"#end_subordinateObject_fiber{loopid}"
    else: 
        raise NameError('Unknown SF component type.')
    
    for i in reversed(range(0,len(index),1)):
        for line in reversed(component_lines):
            lines.insert(index[i]+1,line)

    nlineMod=len(component_lines)*len(index)
    return lines,nlineMod

def reset_odf(lines, index):
    nlineMod = 0
    for ind in index:
        nlineMod += 1
        line = lines[ind].strip().split()
        for i in range(0, len(line)):
            line[i] = '1.0'
        lines[ind] = " ".join(line)
    return lines, nlineMod


def template_dict():
    d = dict()
    d['Background'] = '_riet_par_background_pol'
    d['Intensity'] = '_pd_proc_intensity_incident'
    d['ODFValues'] = '_rita_wimv_odf_values'
    d['SF'] = '#subordinateObject_Standard Functions'
    d['ODFRefine'] = '_rita_odf_refinable'
    d['MainObject'] = '#subordinateObject_'
    d['MicroStrain'] = '_riet_par_rs_microstrain'
    d['CrystSize'] = '_riet_par_cryst_size'
    d['DetPosX'] = '_inst_ang_calibration_center_x'
    d['DetPosY'] = '_inst_ang_calibration_center_y'
    d['DetPosDist'] = '_pd_instr_dist_spec/detc'
    d['Biso'] = '_atom_site_B_iso_or_equiv'
    return d


def add_par(lines, index, endloop):
    nlineMod = 0
    for i in reversed(range(0, len(index))):
        if endloop[i]:
            nlineMod += 1
            lines.insert(index[i]+1, '0 #min -10000.0 #max 10000.0\n')

    return lines, nlineMod


def rem_par(lines, index, endloop):
    nlineMod = 0
    for i in reversed(range(0, len(index))):
        if endloop[i]:
            nlineMod += 1
            lines.pop(index[i])

    return lines, nlineMod


def get_arguments(argsin):
    # Parse user arguments
    welcome = "This is an interface for modifying refinements in MAUD accross one\
               or many simulations. Modifications are applied to all all files \
               matching .par name in the working work_dir and subdirectories."

    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--work_dir', '-d',
                        help='Relative path to work_dir to apply modifications to')
    parser.add_argument('--key', '-k', required=True, nargs='+', action='append',
                        help='Valid Keys: Background, Intensity, ODFValues,ODFRefine,MicroStrain, CrystSize, DetPosX, DetPosY, DetPosDist, Biso, or userdefined (e.g. _riet_par_spec_displac_x)')
    parser.add_argument('--ifile', '-i', required=True,
                        help='Define input file to modify e.g "Initial.par"')
    parser.add_argument('--ofile', '-o',
                        help='Define output file to save modifications e.g. "Refinement_1.par"')
    parser.add_argument('--task', '-t',
                        help='Tasks: free_par,fix_par,set_par,fix_all,ref_par,un_ref_par,add_par,rem_par,reset_odf,add_sf_spherical,add_sf_fiber,track_par,untrack_par,untrack_all')
    parser.add_argument('--sobj', '-s', nargs='+', action='append',
                        help='Subordinate object string limits application of task to a sub section of the .par files')
    parser.add_argument('--nsobj', '-ns', nargs='+', action='append',
                        help='Subordinate object string excludes application of task to a sub section of the .par files')
    parser.add_argument('--value', '-v', nargs='+',
                        help='Value of parameter e.g. for ')
    parser.add_argument('--loopid', '-l', default='None',
                        help='Loop id for modifying loop variables ')
    parser.add_argument('--run_dir', '-dir',
                        help='Base directory from which sub folders are defined and par files are searched for')
    parser.add_argument('--wild', '-n', type=int, nargs='+',
                        help='used with sub_folder (wild) e.g. 1 3 5 would result in a list [1 3 5]')
    parser.add_argument('--wild_range', '-nr', type=int, nargs='+',
                        help='used with sub_folder (wild) and specified in pairs e.g. 1 4 8 9 would result in a list [1 2 3 4 8 9]')
    parser.add_argument('--reverse_search', '-rs', type=str, default='False',
                        help='revereses the parameter search so that it starts at the end')
    parser.add_argument('--max_search_hits', '-mh', type=int, default=1e6,
                        help='exits search_list early based on number of hits')
    parser.add_argument('--verbose', '-ver', type=int, default=0,
                        help='specifies the level of information output when modifying parameter files')
    parser.add_argument('--zfill', type=int, default=3,
                        help='number zero padding the folders.')
    if argsin == []:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argsin.split(' '))

    # Set the working work_dir
    if args.work_dir == None:
        args.work_dir = os.getcwd()

    # Get wild cases if any and combine range and wild
    wilds = []
    if args.wild != None:
        for i in args.wild:
            wilds.append(i)

    if args.wild_range != None:
        for pair in range(0, len(args.wild_range), 2):
            tmp_id = range(args.wild_range[pair], args.wild_range[pair+1]+1)
            for i in tmp_id:
                wilds.append(i)
    wilds = list(set(wilds))

    #path of outfile
    

    # Build input file paths
    ifile = []
    tmp = os.path.join(args.work_dir, args.run_dir, args.ifile)
    if wilds==[] or '(wild)' not in tmp:
        ifile.append(tmp)
    else:
        for wild in wilds:
            ifile.append(tmp.replace('(wild)', str(wild).zfill(args.zfill)))


    #Generate output names
    ofile=[]
    if args.ofile == None:
        args.ofile = ifile
        args.ofile_return = args.ifile
    else:
        args.ofile_return=args.ofile
        tmp = os.path.join(args.work_dir, args.run_dir, args.ofile)
        if wilds==[] or '(wild)' not in tmp:
            ofile.append(tmp)
        else:
            for wild in wilds:
                ofile.append(tmp.replace('(wild)', str(wild).zfill(args.zfill)))
        args.ofile = ofile

    args.ifile = ifile

    if args.sobj == None:
        args.sobj = [[None]]
    else:
        tmp = []
        for sobj1 in args.sobj:
            tmp2 = []
            for sobj2 in sobj1:
                tmp2.append(sobj2.replace('&', ' '))
            tmp.append(tmp2)
        args.sobj = tmp

    if args.nsobj == None:
        tmp = []
        for i in range(0, len(args.sobj)):
            tmp.append([None])
        args.nsobj = tmp
    else:
        tmp = []
        for nsobj1 in args.nsobj:
            tmp2 = []
            for nsobj2 in nsobj1:
                tmp2.append(nsobj2.replace('&', ' '))
            tmp.append(tmp2)
        args.nsobj = tmp

    #Allow for spaces in keys and values
    args.key = [[key.replace('&',' ')] for keys in args.key for key in keys]
    if args.value is not None:
        for i,value in enumerate(args.value):
            args.value[i] = value.replace('&',' ')
    assert len(args.nsobj) == len(args.sobj), 'There is an issue constructing nsobj or sobj'

    # Make sure arguments make sense
    if args.task == 'set_par':
        assert args.value != None, 'must pass a value argument to set a parameter!'
        #Handle value formating
        for i, val in enumerate(args.value):
            try:
                if float(val).is_integer():
                    args.value[i] = f'{int(val)}' 
                else:
                    args.value[i] = f'{float(val):G}' 
            except ValueError:
                pass

    # Make sure arguments make sense
    if args.task == 'ref_par':
        assert args.value != None, 'must pass a multiple and addition to reference another parameter'

    # if args.task=='add_par' or args.task=='rem_par':
    #    assert args.loopid!=None, 'only allowed tosduld only do this for backgrounds..'
    if args.reverse_search in 'True':
        args.reverse_search=True
    else:
        args.reverse_search=False
        
    return args


def getStats(linesMod, nlinesMod, ifile, key):

    nfree = 0
    for ind, line in enumerate(linesMod):
        indstart = line.find('(')
        if indstart > -1 and '#min' in line:
            nfree += 1
    print('========================')
    print('changing key: '+str(key))
    print('changes saved to file: '+ifile)
    print(str(nlinesMod)+' lines were changed')
    print(str(nfree)+' parameters are free')

def add_datafile_background_keys(lines,d,sobj,nsobj):
    
    lines_to_insert=[
        '\n',
        'loop_\n',
        f'{d["Background"]}\n',
        '0 #min -10000.0 #max 10000.0\n'
        ]
    
    #Clean sobj filtering
    if nsobj[0] is None or nsobj[0] == "None":
        nsobj=[]
    if sobj[0] is None or sobj[0] == "None":
        sobj=[]

    #Get index to insert lines if no background already there for datafile
    insert_index=[]
    insert_index_exists=[]
    is_datafile=[]
    sobj_cur=[]
    sobj_index=[]

    for i, line in enumerate(lines):
        # keep track of the subordinate objects
        if 'subordinateObject' in line:
            if 'end' in line:
                is_datafile.pop()
                sobj_cur.pop()
            else:
                is_datafile.append(False)     
                sobj_cur.append(line.partition('subordinateObject')[2])
                              
        if "_riet_meas_datafile_compute" in line and is_datafile!=[]:
            sub_text = ''.join(sobj_cur)
            if all(x not in sub_text for x in nsobj) and all(x in sub_text for x in sobj):               
                #Get potential index to insert lines_to_insert 
                ind = i + 1
                line = lines[ind]
                while bool(line.strip()):
                    ind = ind+1
                    line = lines[ind]
               
                is_datafile[-1]=True   
                insert_index.append(ind)


        if d["Background"] in line and is_datafile[-1]:
            #Update the index to the end of the background loop              
            ind = i + 1
            line = lines[ind]
            while bool(line.strip()):
                ind = ind+1
                line = lines[ind]
            insert_index_exists.append(ind)
            insert_index[-1]=ind

    #Insert background loop where missing
    nlines=0
    for index in reversed(insert_index):
        if index in insert_index_exists:
            nlines+=1
            lines.insert(index,lines_to_insert[-1])
        else:
            for line in reversed(lines_to_insert):
                nlines+=1
                lines.insert(index,line)
    return lines,nlines

def main(argsin,lines=None,do_write=True):
    # Get arguments from user
    args = get_arguments(argsin)

    # Get the dictionary of standard edits
    d = template_dict()

    if lines is None:
        do_read = True
    else:
        assert len(args.ifile)==1, "Only one ifile should be specified when using stored parameter file." 
        do_read = False

    for ifile, ofile in zip(args.ifile,args.ofile): 
        # Main loop through files to edit
        # read in the lines
        if do_read:
            lines = read_par(ifile)

        index = []
        sobj_index = []
        isloop_index = []
        indloop_index = []
        endloop_index = []
        for i in range(0, len(args.key)):
            key = args.key[i][0]
            # Search list of line strings for keyword
            if key in d:
                keyword = d[key]
            else:
                keyword = key

            if args.task=='add_datafile_bk_par':
                linesMod,nlinesMod = add_datafile_background_keys(lines,d,args.sobj[i],args.nsobj[i])
            else:
                if args.reverse_search:
                    tmp = search_list_reverse(lines, keyword, d,args.max_search_hits)
                else:
                    tmp = search_list(lines, keyword, d, args.max_search_hits)
                index.append(tmp[0])
                sobj_index.append(tmp[1])
                isloop_index.append(tmp[2])
                indloop_index.append(tmp[3])
                endloop_index.append(tmp[4])

                # Filter keyword by subordinate object
                if args.sobj[i][0] == 'First':
                    index[i] = [index[i][0]]
                    isloop_index[i] = [isloop_index[i][0]]
                    indloop_index[i] = [indloop_index[i][0]]
                    endloop_index[i] = [endloop_index[i][0]]
                else:
                    if args.nsobj[i][0] == 'First':
                        index[i]=index[i][1:]
                        isloop_index[i]=isloop_index[i][1:]
                        indloop_index[i]=indloop_index[i][1:]
                        endloop_index[i]=endloop_index[i][1:]
                        
                    if args.sobj[i][0] != None and args.sobj[i][0] != 'None':
                        indextmp = []
                        isloop_indextmp = []
                        indloop_indextmp = []
                        endloop_indextmp = []
                        sobj_indextmp = []
                        for j in range(0, len(index[i])):
                            sobjs = ''.join(sobj_index[i][j])
                            if all(x in sobjs for x in args.sobj[i]):
                                # print(sobjs)
                                indextmp.append(index[i][j])
                                isloop_indextmp.append(isloop_index[i][j])
                                indloop_indextmp.append(indloop_index[i][j])
                                endloop_indextmp.append(endloop_index[i][j])
                                sobj_indextmp.append(sobj_index[i][j])
                        index[i] = indextmp
                        isloop_index[i] = isloop_indextmp
                        indloop_index[i] = indloop_indextmp
                        endloop_index[i] = endloop_indextmp
                        sobj_index[i] = sobj_indextmp
                    if args.nsobj[i][0] != None and args.nsobj[i][0] != 'None':
                        indextmp = []
                        isloop_indextmp = []
                        indloop_indextmp = []
                        endloop_indextmp = []
                        for j in range(0, len(index[i])):
                            sobjs = ''.join(sobj_index[i][j])
                            if all(x not in sobjs for x in args.nsobj[i]):
                                # print(sobjs)
                                indextmp.append(index[i][j])
                                isloop_indextmp.append(isloop_index[i][j])
                                indloop_indextmp.append(indloop_index[i][j])
                                endloop_indextmp.append(endloop_index[i][j])
                        index[i] = indextmp
                        isloop_index[i] = isloop_indextmp
                        indloop_index[i] = indloop_indextmp
                        endloop_index[i] = endloop_indextmp

        lines = lines

        # Apply the specified task
        if args.task == 'free_par':
            tmp = free_parameter(lines, index[0], isloop_index[0], indloop_index[0], args.loopid)
        elif args.task == 'fix_par':
            tmp = fix_parameter(lines, index[0], isloop_index[0], indloop_index[0], args.loopid)
        elif args.task == 'set_par':
            tmp = set_par(lines, args.value, index[0],
                        isloop_index[0], indloop_index[0], args.loopid)
        elif args.task == 'fix_all':
            tmp = fix_all(lines)
        elif args.task == 'reset_odf':
            tmp = reset_odf(lines, index[0])
        elif args.task == 'ref_par':
            tmp = ref_par(lines, index, args.value, isloop_index, indloop_index, args.loopid)
        elif args.task == 'add_par':
            tmp = add_par(lines, index[0], endloop_index[0])
        elif args.task == 'rem_par':
            tmp = rem_par(lines, index[0], endloop_index[0])
        elif args.task == 'un_ref_par':
            raise NameError('key is not implemented')
        elif args.task == 'track_par':
            tmp = track_par(lines, index[0], isloop_index[0], indloop_index[0], args.loopid)
        elif args.task == 'untrack_par':
            tmp = untrack_par(lines, index[0], isloop_index[0], indloop_index[0], args.loopid)
        elif args.task == 'untrack_all':
            tmp = untrack_all(lines)
        elif args.task == 'get_phases':
            return get_phases(lines, index[0])
        elif args.task == 'get_key':
            return get_key_value(lines, index[0], isloop_index[0], indloop_index[0], args.loopid, sobj_index[0],keyword)
        elif args.task == 'get_val':
            return get_val(lines, index[0], isloop_index[0], indloop_index[0], args.loopid)
        elif args.task == 'get_err':
            return get_err(lines, index[0], isloop_index[0], indloop_index[0], args.loopid)
        elif args.task == 'add_sf_spherical' or args.task == 'add_sf_fiber':
            tmp = add_sf_component(lines,index[0],args.task,args.loopid)
        elif args.task == 'add_datafile_bk_par':
            pass
        else:
            raise NameError('key is not implemented')
        if args.task !='add_datafile_bk_par':
            linesMod = tmp[0]
            nlinesMod = tmp[1]

        # write back the par
        if do_write:
            write_par(linesMod, ofile)

        if args.verbose > 0:
            getStats(linesMod, nlinesMod, ifile, args.key[0])

    return args.ofile_return

if __name__ == '__main__':
    main([])
