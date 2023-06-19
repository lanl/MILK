import os

fname = os.path.join('fecu.ins')
fID = open(fname, "w")

fID.write('_maud_working_directory\n')
fullpath = r'\'' + os.getcwd() + '/\'\n'
fID.write(fullpath)
fID.write('\n')
fID.write('loop_\n')
fID.write('_riet_analysis_file\n')
fID.write('_riet_analysis_iteration_number\n')
fID.write('_riet_analysis_wizard_index\n')
fID.write('_riet_analysis_fileToSave\n')
fID.write('_riet_meas_datafile_name\n')
fID.write('_riet_append_simple_result_to\n')
fID.write('\'FeCustart.par\' 7 13 \'FECU1010.par\' \'FECU1010.UDF\' \'FECUresults.txt\'\n')

fID.close() 