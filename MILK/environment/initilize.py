#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 10:41:30 2021

@author: danielsavage
"""

import shutil
import configparser
import ast
from pathlib import Path
import os
import sys


class datatype:
    def __init__(self, data_format=None):
        self.data_format = data_format


class folders:
    def __init__(self):
        self.run_dirs = None
        self.work_dir = None
        self.sub_dir = None
        self.wild = None
        self.wild_range = None


class ins:
    def __init__(self):
        self.verbose = None
        self.paths_absolute = None
        self.riet_analysis_file = None
        self.riet_analysis_fileToSave = None
        self.section_title = None
        self.analysis_iteration_number = None
        self.LCLS2_detector_config_file = None
        self.LCLS2_Cspad0_original_image = None
        self.LCLS2_Cspad0_dark_image = None
        self.output_plot2D_filename = None
        self.output_PF_filename = None
        self.output_PF = None
        self.append_simple_result_to = None
        self.append_result_to = None
        self.import_phase = None
        self.ins_file_name = None


class interface:
    def __init__(self, verbose=None):
        self.verbose = None


class compute:
    def __init__(self):
        self.n_maud = None
        self.maud_path = None
        self.clean_old_step_data = None
        self.cur_step = None
        self.log_consol = None


class hippo:
    def __init__(self):
        self.omega_meas = None
        self.chi_meas = None
        self.phi_meas = None
        self.omega_samp = None
        self.chi_samp = None
        self.phi_samp = None
        self.rot_names = None
        self.banks = None
        self.banks_remove = None
        self.detectors = None
        self.data_range = None
        self.data_dir = None
        self.template_name = None
        self.dspacing = None


class lcls:
    def __init__(self):
        self.data_dir = None
        self.template_name = None
        self.group_name = None
        self.z_samp = None
        self.omega_samp = None
        self.chi_samp = None
        self.phi_samp = None


class ini:
    def __init__(self):
        self.folders = folders()
        self.datatype = datatype()
        self.ins = ins()
        self.interface = interface()
        self.compute = compute()
        self.hippo = hippo()
        self.lcls = lcls()
        self.step_num = 1


def resource_file_path(filename):
    for d in sys.path:
        filepath = os.path.join(d, filename)
        if os.path.isfile(filepath):
            return filepath
    return None


def resource_folder_path(folder):
    for d in sys.path:
        folderpath = os.path.join(d, folder)
        if os.path.isdir(folderpath):
            return folderpath
    return None


def initializeTmp(par_input, par_tmp_name):

    shutil.copyfile(par_input, par_tmp_name)


def loadini(fname):
    # Initialize the config
    config = ini()

    # Test to see if ini is in directory
    fname_path = os.path.join(os.getcwd(), fname)
    myfile = Path(fname_path)
    if not myfile.exists():
        script_path = os.path.dirname(os.path.realpath(__file__))
        template_path = os.path.join(script_path, 'resources/template.ini')
        shutil.copyfile(template_path, fname_path)

    # Takes as input a .ini file
    configtmp = configparser.ConfigParser()
    configtmp.read(fname)

    # Import data type option
    datatype = configtmp['DATATYPE']
    config.datatype.data_format = datatype.get('data_format')

    # Import the ins options
    ins = configtmp['INS']
    config.ins.paths_absolute = ins.get('paths_absolute')
    config.ins.riet_analysis_file = ins.get('riet_analysis_file')
    config.ins.riet_analysis_fileToSave = ins.get('riet_analysis_fileToSave')
    config.ins.section_title = ins.get('section_title')
    config.ins.analysis_iteration_number = ins.getint('analysis_iteration_number')
    config.ins.LCLS2_detector_config_file = ins.get('LCLS2_detector_config_file')
    config.ins.LCLS2_Cspad0_original_image = ins.get('LCLS2_Cspad0_original_image')
    config.ins.LCLS2_Cspad0_dark_image = ins.get('LCLS2_Cspad0_dark_image')
    config.ins.maud_remove_all_datafiles = ins.get('maud_remove_all_datafiles')
    config.ins.output_plot2D_filename = ins.get('output_plot2D_filename')
    config.ins.output_PF_filename = ins.get('output_PF_filename')
    config.ins.output_PF = ins.get('output_PF')
    config.ins.append_simple_result_to = ins.get('append_simple_result_to')
    config.ins.append_result_to = ins.get('append_result_to')
    config.ins.import_phase = ast.literal_eval(ins.get('import_phase'))
    config.ins.ins_file_name = ins.get('ins_file_name')
    config.ins.verbose = ins.getint('verbose')

    # copy phases to current directory
    for phase in config.ins.import_phase:
        fname_path = os.path.join(os.getcwd(), phase)
        myfile = Path(fname_path)
        if not myfile.exists():
            resource_path = resource_file_path('resources/cif/'+phase)

            if resource_path != None:
                shutil.copyfile(resource_path, phase)
            else:
                raise NameError('Unable to find phase: '+phase)

    if config.datatype.data_format == 'HIPPO':
        hippo = configtmp['HIPPO']
        config.hippo.omega_meas = ast.literal_eval(hippo.get('omega_meas'))
        config.hippo.chi_meas = ast.literal_eval(hippo.get('chi_meas'))
        config.hippo.phi_meas = ast.literal_eval(hippo.get('phi_meas'))
        config.hippo.omega_samp = ast.literal_eval(hippo.get('omega_samp'))
        config.hippo.chi_samp = ast.literal_eval(hippo.get('chi_samp'))
        config.hippo.phi_samp = ast.literal_eval(hippo.get('phi_samp'))
        config.hippo.rot_names = ast.literal_eval(hippo.get('rot_names'))
        config.hippo.detectors = ast.literal_eval(hippo.get('detectors'))
        config.hippo.banks = ast.literal_eval(hippo.get('banks'))
        config.hippo.banks_remove = ast.literal_eval(hippo.get('banks_remove'))
        config.hippo.data_range = ast.literal_eval(hippo.get('data_range'))
        config.hippo.data_dir = hippo.get('data_dir')
        config.hippo.template_name = hippo.get('template_name')
        config.hippo.dspacing = ast.literal_eval(hippo.get('dspacing'))

        assert len(config.hippo.omega_meas) == len(
            config.hippo.chi_meas), 'Length omega_meas must be same as chi_meas and phi_meas'
        assert len(config.hippo.omega_meas) == len(
            config.hippo.phi_meas), 'Length omega_meas must be same as chi_meas and phi_meas'
        assert len(config.hippo.omega_meas) == len(
            config.hippo.rot_names), 'Length omega_meas must be same as rot_name'
        assert len(config.hippo.detectors) == len(
            config.hippo.banks), 'Length banks must be same as detectors'
        assert len(config.hippo.detectors) == len(
            config.hippo.dspacing), 'Length banks must be same as dspacing ranges'

        # copy hippo template to current directory
        fname_path = os.path.join(os.getcwd(), config.hippo.template_name)
        myfile = Path(fname_path)
        if not myfile.exists():

            fname = str(len(config.hippo.omega_meas))+'_rotations.par'
            if fname != config.hippo.template_name:
                print('Unable to find specified file. Using generic template')

            resource_path = os.path.join(os.path.dirname(
                __file__), 'resources/templates/HIPPO', fname)

            myfile = Path(resource_path)
            if myfile.exists():
                shutil.copyfile(resource_path, config.hippo.template_name)
            else:
                raise NameError('Unable to find generic template: '+fname)

        # find data directory
        fname_path = os.path.join(os.getcwd(), config.hippo.data_dir)
        myfile = Path(fname_path)
        if not myfile.exists():
            raise NameError('Unable to find data directory')

    elif config.datatype.data_format == 'LCLS':
        lcls = configtmp['LCLS']
        config.lcls.template_name = lcls.get('template_name')
        # config.lcls.data_dir=lcls.get('data_dir')
        # config.lcls.group_name=ast.literal_eval(lcls.get('group_name'))
        # config.lcls.omega_samp=ast.literal_eval(lcls.get('omega_samp'))
        # config.lcls.chi_samp=ast.literal_eval(lcls.get('chi_samp'))
        # config.lcls.phi_samp=ast.literal_eval(lcls.get('phi_samp'))
        # config.lcls.z_samp=ast.literal_eval(lcls.get('z_samp'))
        # #copy lcls template to current directory
        # fname_path=os.path.join(os.getcwd(),config.lcls.template_name)
        # myfile=Path(fname_path)
        # if not myfile.exists():

        #     fname='template.par'
        #     if fname!=config.lcls.template_name:
        #         print('Unable to find specified file. Using generic template')

        #     resource_path=os.path.join(os.path.dirname(__file__),'resources/templates/LCLS',fname)

        #     myfile=Path(resource_path)
        #     if myfile.exists():
        #         shutil.copyfile(resource_path, config.lcls.template_name)
        #     else:
        #         raise NameError('Unable to find generic template: '+fname)

    elif config.datatype.data_format == '2DXRD':
        raise NameError('Unimplemented data format')
    else:
        raise NameError('Unsupported data format')

    # Import the folder options
    folders = configtmp['FOLDERS']
    config.folders.run_dirs = folders.get('run_dirs')
    config.folders.work_dir = folders.get('work_dir')
    config.folders.sub_dir = folders.get('sub_dir')
    config.folders.wild = ast.literal_eval(folders.get('wild'))
    config.folders.wild_range = ast.literal_eval(folders.get('wild_range'))

    # Import the compute options
    compute = configtmp['COMPUTE']
    config.compute.maud_path = compute.get('maud_path')
    config.compute.clean_old_step_data = compute.get('clean_old_step_data')
    config.compute.cur_step = compute.get('cur_step')
    config.compute.n_maud = compute.getint('n_maud')
    config.compute.log_consol = compute.getboolean('log_consol')

    # Import the interface options
    interface = configtmp['INTERFACE']
    config.interface.verbose = interface.getint('verbose')

    return config


if __name__ == '__main__':
    loadini()
