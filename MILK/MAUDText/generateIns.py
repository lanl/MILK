#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 11:34:24 2020

@author: danielsavage
"""
import argparse
import os
import shutil


def maud_ins_dictionary():
    # The list of things we can do in the in the script
    d = {'riet_analysis_file': '',
         'publ_section_title': '',
         'riet_analysis_iteration_number': '',
         'riet_analysis_wizard_index': '',
         'maud_remove_all_datafiles': '',
         'riet_analysis_fileToSave': '',
         'maud_LCLS2_detector_config_file': '',
         'maud_LCLS2_Cspad0_original_image': '',
         'maud_LCLS2_Cspad0_dark_image': '',
         'maud_output_plot_filename': '',
         'maud_output_plot2D_filename': '',
         'maud_output_summed_data_filename': '',
         'maud_export_pole_figures_filename': '',
         'maud_export_pole_figures': '',
         'riet_append_simple_result_to': '',
         'maud_import_phase': '',
         'riet_append_result_to': ''}
    return d


def write_ins(args):

    # Get the accept args to print to ins file
    d = maud_ins_dictionary()

    # write a single ins file for use with the gui
    # fname=os.path.join(args.work_dir[0][0],args.ins_file_name[0][0].split('/')[-1])
    #fID = open(fname, "w")

    # write cif loop header
    # fID.write('loop_\n')
    # for arg in vars(args):
    #    argtmp=getattr(args, arg)
    #    if argtmp!=None and arg in d:
    #        for blah in argtmp[0]:
    #            fID.write('_%s\n' % str(arg))
    # fID.write('\n')

    # Loop over the runid
    # for i in range(0,len(args.wild)):
    #     #write the main outputs
    #     for arg in vars(args):
    #         argattr=getattr(args, arg)
    #         if argattr!=None and arg in d:
    #             if arg=='riet_analysis_file' and not (args.paths_absolute[0][0]=='True' or args.paths_absolute[0][0]=='true'):
    #                parname='tmp'+str(i).zfill(3)+'.par'
    #                if i==0:
    #                    parname=os.path.join(args.work_dir[0][0],parname)
    #                shutil.copyfile(os.path.join(args.work_dir[0][0],argattr[0][0]),parname)
    #                fID.write(' \'%s\'' % parname)
    #             elif arg=='riet_analysis_wizard_index' or arg=='riet_analysis_iteration_number' or arg=='maud_remove_all_datafiles':
    #                 for arg in argattr[i]:
    #                     fID.write(' %s' % arg)
    #             elif type(argattr[i]) is list:
    #                 for arg in argattr[i]:
    #                     fID.write(' \'%s\'' % arg)
    #             else:
    #                 fID.write(' \'%s\'' % argattr[i])
    #     fID.write('\n')
    # fID.close()

    # write an ins to each folder for commandline MAUD
    # Loop over the runid
    for i in range(0, len(args.wild)):
        # open the ins file to write
        fname = os.path.join(args.ins_file_name[i][0])
        fID = open(fname, "w")

        # write cif loop header
        fID.write('loop_\n')
        for arg in vars(args):
            argtmp = getattr(args, arg)
            if argtmp != None and arg in d:
                for blah in argtmp[i]:
                    fID.write('_%s\n' % str(arg))
        fID.write('\n')

        # write the main outputs
        for arg in vars(args):
            argattr = getattr(args, arg)
            if argattr != None and arg in d:
                # if arg=='riet_analysis_file' and not (args.paths_absolute[0][0]=='True' or args.paths_absolute[0][0]=='true'):
                #    parname='tmp'+str(i).zfill(3)+'.par'
                #    shutil.copyfile(os.path.join(args.work_dir[0][0],argattr[0][0]),parname)
                #    fID.write(' \'%s\'' % parname)
                if arg == 'riet_analysis_wizard_index' or arg == 'riet_analysis_iteration_number':
                    for arg in argattr[i]:
                        fID.write(' %s' % arg)
                elif type(argattr[i]) is list:
                    for arg in argattr[i]:
                        fID.write(' \'%s\'' % arg)
                else:
                    fID.write(' \'%s\'' % argattr[i])
        fID.close()


def build_ins(args):

    # Generate the working directory
    if args.work_dir != None:
        args.work_dir = args.work_dir[0][0]
    else:
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

    wild = list(set(wilds))
    setattr(args, 'wild', wild)

    # Setup the paths
    if args.paths_absolute == 'True' or args.paths_absolute == 'true':
        args.riet_analysis_file = os.path.join(
            args.work_dir, args.run_dir, args.sub_dir, args.riet_analysis_file)
        args.riet_analysis_fileToSave = os.path.join(
            args.work_dir, args.run_dir, args.sub_dir, args.riet_analysis_fileToSave)
        args.riet_append_result_to = os.path.join(
            args.work_dir, args.run_dir, args.sub_dir, args.riet_append_result_to)
        args.riet_append_simple_result_to = os.path.join(
            args.work_dir, args.run_dir, args.sub_dir, args.riet_append_simple_result_to)
        if args.maud_export_pole_figures_filename != None:
            args.maud_export_pole_figures_filename = os.path.join(
                args.work_dir, args.run_dir, args.sub_dir, args.maud_export_pole_figures_filename)
            args.maud_export_pole_figures = " ".join(args.maud_export_pole_figures)
        if args.maud_output_plot2D_filename != None:
            args.maud_output_plot2D_filename = os.path.join(
                args.work_dir, args.run_dir, args.sub_dir, args.maud_output_plot2D_filename)
        args.ins_file_name = os.path.join(
            args.work_dir, args.work_dir, args.run_dir, args.sub_dir, args.ins_file_name)
        if args.maud_import_phase != None:
            for i, phase in enumerate(args.maud_import_phase):
                args.maud_import_phase[i] = os.path.join(args.work_dir, phase)
    else:
        args.work_dir = os.path.join(args.work_dir, args.run_dir, args.sub_dir)
        if args.maud_import_phase != None:
            for i, phase in enumerate(args.maud_import_phase):
                args.maud_import_phase[i] = os.path.join('..', phase)
        args.riet_analysis_file = os.path.join(args.work_dir, args.riet_analysis_file)
        args.riet_analysis_fileToSave = args.riet_analysis_fileToSave
        args.riet_append_result_to = args.riet_append_result_to
        args.riet_append_simple_result_to = args.riet_append_simple_result_to
        if args.maud_export_pole_figures_filename != None:
            args.maud_export_pole_figures_filename = args.maud_export_pole_figures_filename
            args.maud_export_pole_figures = " ".join(args.maud_export_pole_figures)
        if args.maud_output_plot2D_filename != None:
            args.maud_output_plot2D_filename = args.maud_output_plot2D_filename
        args.ins_file_name = os.path.join(args.work_dir, args.ins_file_name)

    # for each arg build a list of length wild that will be printed to files
    for arg in vars(args):
        argattr = getattr(args, arg)
        argattrstr = str(argattr)
        if argattrstr != 'None':
            if type(argattr) is list and arg != 'maud_export_pole_figures':
                tmp = []
                for i, rid in enumerate(wild):
                    tmp2 = []
                    for j, argattrl in enumerate(argattr):
                        argattrstr = str(argattrl)
                        tmp2.append(argattrstr.replace('(wild)', str(rid).zfill(3)))
                    tmp.append(tmp2)
                setattr(args, arg, tmp)
            else:
                tmp = []
                for i, rid in enumerate(wild):
                    tmp2 = [argattrstr.replace('(wild)', str(rid).zfill(3))]
                    tmp.append(tmp2)
                setattr(args, arg, tmp)

    # Need to search for LCLS2 image for import
    if args.sub_dir != None:
        # Look for LCLS2_Cspad0_original_image if specified
        # This assumes 1 Cspad0 image per directory
        if args.maud_LCLS2_Cspad0_original_image != None:
            if 'search' in args.maud_LCLS2_Cspad0_original_image[0]:
                tmp = []
                for i in range(0, len(wild)):
                    fullpath = os.path.join(
                        args.work_dir[i][0], args.run_dir[i][0], args.sub_dir[i][0])
                    for f in os.listdir(fullpath):
                        if 'Cspad-0' in f and '.tiff' in f and 'MecTargetChamber' in f:
                            tmp.append([os.path.join(fullpath, f)])
                setattr(args, 'maud_LCLS2_Cspad0_original_image', tmp)

    return args


def get_arguments(argsin):
    # Parse user arguments
    welcome = "This is an interface for generating .ins files for MAUD batch processing"

    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--riet_analysis_file', '-a', required=True,
                        help='The input parameter file used as a starting point for the batch analysis. e.g. Initial.par')
    parser.add_argument('--riet_analysis_fileToSave', '-s', required=True,
                        help='A .par file name for all analysis to be saved to e.g. Initial_(wild).par or Initial.par. In the case that wild is not specified all analysis will be saved with same name but in the directory(s) specified by sub folder')
    parser.add_argument('--riet_analysis_iteration_number', '-i', required=True,
                        help='The number of iterations in a reitveld step e.g. 4')
    parser.add_argument('--ins_file_name', '-o', required=True,
                        help='Name for the ins file name. If multiple wild, make sure to include wild in name!')
    parser.add_argument('--publ_section_title', '-p',
                        help='Name of analysis in the refinement. This names the analysis in results files e.g. run(wild) or runAwesomeness')
    parser.add_argument('--riet_analysis_wizard_index', '-w',
                        help='Specifies the MAUD wizard refinement number e.g. specifying 1 refinements background and intensity')
    parser.add_argument('--maud_remove_all_datafiles', '-r',
                        help='Removes intensity data and detectors(?) from par file so that data is read in')
    parser.add_argument('--maud_LCLS2_detector_config_file', '-LCLS2_conf',
                        help='Must be a relative path to working dir e.g.//LCLS2_config_data2.cif')
    parser.add_argument('--maud_LCLS2_Cspad0_original_image', '-LCLS2_OI',
                        help='Must be a relative path to working dir e.g. //run/preshock/MecTargetChamber-0-Cspad-0-r0339-20131109-191841.045455907.tiff. Use search to auto populate this if only one Cspad-0 in directory')
    parser.add_argument('--maud_LCLS2_Cspad0_dark_image', '-LCLS2_DI',
                        help='Must be a relative path to working dir e.g. //LCLS2_config_data2.cif //calib/CsPad::CalibV1/MecTargetChamber.0:Cspad.0/pedestals/222-372.data')
    parser.add_argument('--riet_append_result_to', '-results',
                        help='Results are parameters specified by autotrace e.g. results.csv')
    parser.add_argument('--riet_append_simple_result_to', '-simple_results',
                        help='Simple results are those prechosen by MAUD i.e. biso, fit, lattice parameter etc... e.g. results_simple.csv')
    parser.add_argument('--work_dir', '-dir',
                        help='Base directory from which sub folders are defined and par files are searched for')
    parser.add_argument('--run_dir', '-rd',
                        help='folders to run job in relative to work_dir /e.g. /run(wild) where (wild) is replaced by the wild and/or wild_range combined lists. wild need not be used')
    parser.add_argument('--sub_dir', '-sf',
                        help='folders to run job in relative to work_dir /e.g. /run(wild)/preshock where (wild) is replaced by the wild and/or wild_range combined lists. wild need not be used')
    parser.add_argument('--wild', '-n', type=int, nargs='+',
                        help='used with sub_dir (wild) e.g. 1 3 5 would result in a list [1 3 5]')
    parser.add_argument('--wild_range', '-nr', type=int, nargs='+',
                        help='used with sub_dir (wild) and specified in pairs e.g. 1 4 8 9 would result in a list [1 2 3 4 8 9]')
    parser.add_argument('--maud_export_pole_figures_filename', '-PF_name',
                        help='absolute path and prefix for polefigures to be saved to. e.g. //somepath/prefix_(wild). wild need not be used')
    parser.add_argument('--maud_export_pole_figures', '-PF', nargs='+',
                        help='specification of poles to export e.g. "p0 0 0 1 1 0 0 1 1 0" "p1 0 0 1 1 0 0 1 1 0" "p2 0 0 1 1 0 0 1 1 0"')
    parser.add_argument('--maud_output_plot_filename', '-plot1d',
                        help='specify path and prefix to store 1D spectra fit images')
    parser.add_argument('--maud_output_plot2D_filename', '-plot2d',
                        help='specify path and prefix to store 2D spectra fit images')
    parser.add_argument('--maud_output_summed_data_filename', '-export_all',
                        help='specify path and prefix to store all spectra in')
    parser.add_argument('--maud_import_phase', '-ip', nargs='+',
                        help='specify full or relative path to cif phase file(s)')
    parser.add_argument('--paths_absolute', '-pa',
                        help='specify whether paths should be relative to work_dir')
    if argsin == []:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argsin.split(' '))

    # Take care of any dependencies
    if args.maud_LCLS2_detector_config_file != None:
        assert args.maud_LCLS2_Cspad0_original_image != None, 'Need to have LCLS2_detector_config_file, maud_LCLS2_Cspad0_original_image,maud_remove_all_datafiles, and maud_LCLS2_Cspad0_dark_image'
        assert args.maud_LCLS2_Cspad0_dark_image != None, 'Need to have LCLS2_detector_config_file, maud_LCLS2_Cspad0_original_image,maud_remove_all_datafiles, and maud_LCLS2_Cspad0_dark_image'
        assert args.maud_remove_all_datafiles != None, 'Need to have LCLS2_detector_config_file, maud_LCLS2_Cspad0_original_image, maud_remove_all_datafiles, and maud_LCLS2_Cspad0_dark_image'

    if args.maud_LCLS2_Cspad0_dark_image != None:
        assert args.maud_LCLS2_Cspad0_original_image != None, 'Need to have LCLS2_detector_config_file, maud_LCLS2_Cspad0_original_image, maud_remove_all_datafiles, and maud_LCLS2_Cspad0_dark_image'
        assert args.maud_LCLS2_detector_config_file != None, 'Need to have LCLS2_detector_config_file, maud_LCLS2_Cspad0_original_image, maud_remove_all_datafiles, and maud_LCLS2_Cspad0_dark_image'
        assert args.maud_remove_all_datafiles != None, 'Need to have LCLS2_detector_config_file, maud_LCLS2_Cspad0_original_image, maud_remove_all_datafiles, and maud_LCLS2_Cspad0_dark_image'

    if args.maud_LCLS2_Cspad0_original_image != None:
        assert args.maud_LCLS2_detector_config_file != None, 'Need to have LCLS2_detector_config_file, maud_LCLS2_Cspad0_original_image, maud_remove_all_datafiles, and maud_LCLS2_Cspad0_dark_image'
        assert args.maud_LCLS2_Cspad0_dark_image != None, 'Need to have LCLS2_detector_config_file, maud_LCLS2_Cspad0_original_image, maud_remove_all_datafiles, and maud_LCLS2_Cspad0_dark_image'
        assert args.maud_remove_all_datafiles != None, 'Need to have LCLS2_detector_config_file, maud_LCLS2_Cspad0_original_image, maud_remove_all_datafiles, and maud_LCLS2_Cspad0_dark_image'

    if args.maud_remove_all_datafiles != None:
        assert args.maud_LCLS2_detector_config_file != None, 'Need to have LCLS2_detector_config_file, maud_LCLS2_Cspad0_original_image, maud_remove_all_datafiles, and maud_LCLS2_Cspad0_dark_image'
        assert args.maud_LCLS2_Cspad0_dark_image != None, 'Need to have LCLS2_detector_config_file, maud_LCLS2_Cspad0_original_image, maud_remove_all_datafiles, and maud_LCLS2_Cspad0_dark_image'
        assert args.maud_LCLS2_Cspad0_original_image != None, 'Need to have LCLS2_detector_config_file, maud_LCLS2_Cspad0_original_image, maud_remove_all_datafiles, and maud_LCLS2_Cspad0_dark_image'

    if args.wild == None and args.wild_range == None:
        args.wild = [0]

    # for arg in vars(args):
    #     print(arg, getattr(args, arg))

    return args


def main(argsin):
    args = get_arguments(argsin)
    args = build_ins(args)
    write_ins(args)


if __name__ == '__main__':
    main([])
