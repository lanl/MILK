#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 08:29:42 2021

@author: danielsavage
"""

from . import generateIns
from . import callMaudText
import shutil


class arguments:
    def __init__(self):
        self.n_maud = None
        self.timeout = None
        self.log_consol = None
        self.maud_path = None
        self.java_opt = None
        self.clean_old_step_data = None
        self.cur_step = None
        self.paths_absolute = None
        self.riet_analysis_file = None
        self.publ_section_title = None
        self.riet_analysis_iteration_number = None
        self.riet_analysis_wizard_index = None
        self.riet_analysis_fileToSave = None
        self.maud_LCLS2_detector_config_file = None
        self.maud_LCLS2_Cspad0_original_image = None
        self.maud_LCLS2_Cspad0_dark_image = None
        self.maud_output_plot2D_filename = None
        self.maud_output_summed_data_filename = None
        self.maud_output_plot_filename = None
        self.maud_export_pole_figures_filename = None
        self.maud_export_pole_figures = None
        self.riet_append_simple_result_to = None
        self.riet_append_result_to = None
        self.maud_import_phase = None
        self.import_phase = None
        self.import_lcls = None
        self.export_PFs = None
        self.export_plots = None
        self.ins_file_name = None
        self.work_dir = None
        self.run_dirs = None
        self.wild = None
        self.wild_range = None
        self.absolute_path = None  # Similar change to always work...
        self.single_file = None  # Change to another option
        self.verboseins = None
        self.ins_for_gui = True
        self.args_ins = None
        self.args_compute = None
        self.maud_remove_all_datafiles = None

    def parseConfig(self, config, cur_step=None):
        self.n_maud = str(config["compute"]["n_maud"])
        self.log_consol = config["compute"]["log_consol"]
        self.maud_path = config["compute"]["maud_path"]
        self.java_opt = config["compute"]["java_opt"]
        if "timeout" in config["compute"]:
            self.timeout = config["compute"]["timeout"]
        self.clean_old_step_data = config["compute"]["clean_old_step_data"]
        if cur_step == None:
            self.cur_step = config["compute"]["cur_step"]
        else:
            self.cur_step = cur_step
        self.paths_absolute = False
        self.riet_analysis_file = config["ins"]["riet_analysis_file"]
        self.publ_section_title = config["ins"]["section_title"].replace(' ','_')
        self.riet_analysis_iteration_number = str(config["ins"]["analysis_iteration_number"])
        self.riet_analysis_fileToSave = config["ins"]["riet_analysis_fileToSave"]
        self.maud_LCLS2_detector_config_file = config["ins"]["LCLS2_detector_config_file"]
        self.maud_LCLS2_Cspad0_original_image = config["ins"]["LCLS2_Cspad0_original_image"]
        self.maud_LCLS2_Cspad0_dark_image = config["ins"]["LCLS2_Cspad0_dark_image"]
        self.maud_output_plot2D_filename = config["ins"]["output_plot2D_filename"]
        self.maud_output_diff_data_filename = config["ins"]["output_summed_data_filename"]
        self.maud_output_plot_filename = config["ins"]["maud_output_plot_filename"]
        self.maud_export_pole_figures_filename = config["ins"]["output_PF_filename"]
        self.maud_export_pole_figures = config["ins"]["output_PF"]
        self.riet_append_simple_result_to = config["ins"]["append_simple_result_to"]
        self.riet_append_result_to = config["ins"]["append_result_to"]
        self.maud_import_phase = config["ins"]["import_phase"]
        self.import_phases = False
        self.import_lcls = False
        self.export_PFs = False
        self.export_plots = False
        self.ins_file_name = config["ins"]["ins_file_name"]
        self.work_dir = config["folders"]["work_dir"]
        self.run_dirs = config["folders"]["run_dirs"]
        self.wild = config["folders"]["wild"]
        self.wild_range = config["folders"]["wild_range"]
        self.verboseins = config["ins"]["verbose"]
        self.maud_remove_all_datafiles = config["ins"]["maud_remove_all_datafiles"]

        #Purge wild_range
        wilds = self.wild
        if self.wild_range!=[[]]:
            for wild_range in self.wild_range:
                wilds+=list(range(wild_range[0],wild_range[1]+1))
        self.wild = list(set(wilds))
        self.wild_range = [[]]

    def parse_arguments_ins(self):
        args = ''
        if self.riet_analysis_file != None:
            args = args+'--riet_analysis_file '+self.riet_analysis_file+' '
        if self.publ_section_title != None:
            args = args+'--publ_section_title ' + \
                self.publ_section_title+str(self.cur_step).zfill(2)+' '
        if self.riet_analysis_iteration_number != None:
            args = args+'--riet_analysis_iteration_number '+self.riet_analysis_iteration_number+' '
        if self.riet_analysis_wizard_index != None and self.riet_analysis_wizard_index != '':
            args = args+'--riet_analysis_wizard_index '+self.riet_analysis_wizard_index+' '
        if self.riet_analysis_fileToSave != None:
            args = args+'--riet_analysis_fileToSave '+self.riet_analysis_fileToSave+' '
        if self.maud_LCLS2_detector_config_file != None and self.maud_LCLS2_detector_config_file != '' and self.import_lcls:
            args = args+'--maud_LCLS2_detector_config_file '+self.maud_LCLS2_detector_config_file+' '
        if self.maud_LCLS2_Cspad0_original_image != None and self.maud_LCLS2_Cspad0_original_image != '' and self.import_lcls:
            args = args+'--maud_LCLS2_Cspad0_original_image '+self.maud_LCLS2_Cspad0_original_image+' '
        if self.maud_LCLS2_Cspad0_dark_image != None and self.maud_LCLS2_Cspad0_dark_image != '' and self.import_lcls:
            args = args+'--maud_LCLS2_Cspad0_dark_image '+self.maud_LCLS2_Cspad0_dark_image+' '
        if self.maud_output_plot2D_filename != None and self.maud_output_plot2D_filename != '' and self.export_plots:
            args = args+'--maud_output_plot2D_filename '+self.maud_output_plot2D_filename+' '
        if self.maud_output_diff_data_filename is not None and self.maud_output_diff_data_filename != '':
            args = args+'--maud_output_diff_data_filename '+self.maud_output_diff_data_filename + ' '
        if self.maud_output_plot_filename is not None and self.maud_output_plot_filename != '' and self.export_plots:
            args = args+'--maud_output_plot_filename '+self.maud_output_plot_filename + ' '
        if self.maud_export_pole_figures_filename != None and self.maud_export_pole_figures_filename != '' and self.export_PFs:
            args = args+'--maud_export_pole_figures_filename '+self.maud_export_pole_figures_filename+' '
        if self.maud_export_pole_figures != None and self.maud_export_pole_figures != '' and self.export_PFs:
            args = args+'--maud_export_pole_figures '+self.maud_export_pole_figures+' '
        if self.maud_remove_all_datafiles != None and self.import_lcls:
            args = args+'--maud_remove_all_datafiles '+f"{self.maud_remove_all_datafiles}"+' '
        if self.riet_append_simple_result_to != None:
            args = args+'--riet_append_simple_result_to '+self.riet_append_simple_result_to+' '
        if self.riet_append_result_to != None:
            args = args+'--riet_append_result_to '+self.riet_append_result_to+' '
        if self.maud_import_phase != None and self.import_phases:
            args = args+'--maud_import_phase '
            for phase in self.maud_import_phase:
                args = args+phase+' '
        if self.ins_file_name != None:
            args = args+'--ins_file_name '+self.ins_file_name+' '
        if self.work_dir != None and self.work_dir != '':
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
        if self.paths_absolute == 'True' or self.paths_absolute == 'true':
            args = args+'--paths_absolute True'+' '
        else:
            args = args+'--paths_absolute False'+' '
        # if self.verboseins!=None:
        #    args=args+'--verbose '+self.verboseins+' '

        # trim at the end
        self.args_ins = args[0:-1]

    def parse_arguments_compute(self):
        args = ''

        if self.n_maud != None:
            args = args+'--nMAUD '+self.n_maud+' '
        if self.timeout != None:
            args = f"{args}--timeout {self.timeout} "
        if self.ins_file_name != None:
            args = args+'--ins_file_name '+self.ins_file_name+' '
        if self.work_dir != None and self.work_dir != '':
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
        if self.maud_path != None and self.maud_path != '':
            args = args+'--maud_path '+self.maud_path+' '
        if self.java_opt != None and self.java_opt != '':
            args = args+'--java_opt '+self.java_opt+' '
        if self.clean_old_step_data != None:
            args = args+'--clean_old_step_data '+str(self.clean_old_step_data)+' '
            self.clean_old_step_data = 'False'
        if self.cur_step != None:
            args = args+'--cur_step '+str(self.cur_step)+' '
        if self.simple_call != None and self.simple_call:
            args = args+'--simple_call True'+' '
        if self.riet_append_simple_result_to != None:
            args = args+'--riet_append_simple_result_to '+self.riet_append_simple_result_to+' '
        if self.riet_append_result_to != None:
            args = args+'--riet_append_result_to '+self.riet_append_result_to+' '

        # trim at the end
        self.args_compute = args[0:-1]


class maudText(arguments):
    def __init__(self):
        super().__init__()

    def refinement(self, itr=None, wizard_index=None, ifile=None, ofile=None,
                   wild=None, wild_range=None, work_dir=None, verboseins=None,
                   verbosecompute=None, n_maud=None, run=True, export_ins=True, import_phases=False,
                   import_lcls=False, export_PFs=False, export_plots=False, inc_step=True,
                   simple_call=False,timeout=None):
        '''
        untracking all parameter outputs and stops there value from being printed in summary document after a refinement unless basic parameter
        Optional inputs:
            loopid   (str): a zero based integer specifying a parameter location in a loop variable. By default all loop values are changed
            sobj     (str): one or more subordinate objects to include in the scope of operation
            nsobj    (str): one or more subordinate objects to exclude in the scope of operation
            run     (bool): specifies whether to apply changes to parameter files
            ifile    (str): input parameter file 
            dir      (str): working directory

        Outputs: 
            Updates editor arguments and applies changes to parameter files if run=True(default)
        '''
        if work_dir != None:
            self.work_dir = work_dir
        if itr != None:
            self.riet_analysis_iteration_number = itr
        if wizard_index != None:
            self.riet_analysis_wizard_index = wizard_index
        else:
            self.riet_analysis_wizard_index = None
        if ifile != None:
            self.riet_analysis_file = ifile
        if ofile != None:
            self.riet_analysis_fileToSave = ofile
        if wild_range != None:
            self.wild_range = wild_range
        if verboseins != None:
            self.verboseins = verboseins
        if verbosecompute != None:
            self.verbosecompute = verbosecompute
        if n_maud != None:
            self.n_maud = n_maud
        if timeout != None:
            self.timeout = timeout
        self.import_phases = import_phases
        self.import_lcls = import_lcls
        self.export_PFs = export_PFs
        self.export_plots = export_plots
        self.simple_call = simple_call

        # parse
        self.parse_arguments_ins()
        self.parse_arguments_compute()
        if export_ins:
            generateIns.main(self.args_ins)
        if run:
            callMaudText.main(self.args_compute)
            if inc_step:
                self.cur_step = str(int(self.cur_step)+1)
