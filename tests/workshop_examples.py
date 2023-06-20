# test_with_unittest.py

import os
import sys
from MILK.data.examples import maudBatch
from MILK.MAUDText import callMaudText
import tempfile
from changeDirectory import cd
from pathlib import Path

# class cd:
#     """Context manager for changing the current working directory"""
#     def __init__(self, newPath):
#         self.newPath = os.path.expanduser(newPath)

#     def __enter__(self):
#         self.savedPath = os.getcwd()
#         os.chdir(self.newPath)

#     def __exit__(self, etype, value, traceback):
#         os.chdir(self.savedPath)

def write_ins(fname='fecu.ins'):
    with open(fname, "w") as fID:
        fID.write('_maud_working_directory\n')

        fullpath = f"{os.getcwd()}{os.sep}"
        if "win" in sys.platform:
            fullpath = fullpath.replace('\\', '\\\\')

        fID.write('\''+fullpath+'\'\n')
        fID.write('\n')
        fID.write('loop_\n')
        fID.write('_riet_analysis_file\n')
        fID.write('_riet_analysis_iteration_number\n')
        fID.write('_riet_analysis_wizard_index\n')
        fID.write('_riet_analysis_fileToSave\n')
        fID.write('_riet_meas_datafile_name\n')
        fID.write('_riet_append_simple_result_to\n')
        fID.write('\'FeCustart.par\' 7 13 \'FECU1010.par\' \'FECU1010.UDF\' \'FECUresults.txt\'\n')

def test_maudbatch1():
    """Tests the first example, "maud batch"
    Writes the customized .ins file for the working directory where maudbatch exists in the 
    operating system format.
    Writes the first run only to be run for test purposes.

    Windows GitHub Runner has special character "runner~1" that causes issues, so not using the temporary diretory.
    """
    if "win" in sys.platform:
        cwdDir = os.getcwd()
        maudBatch(CUR_DIR = cwdDir)
        with cd("maudbatch"):
            write_ins()
            callMaudText.run_MAUD(
                os.getenv('MAUD_PATH').strip("'"),
                "mx8G",
                'False',
                None,
                "fecu.ins")
            files = [ f for f in os.listdir( os.curdir ) if os.path.isfile(f) ]
            print(files)
            with open('fecu.ins') as f:
                lines = f.read()
            print(lines)
            assert 'FECU1010.par' in files
    else:
        with tempfile.TemporaryDirectory() as tmpdirname:
            print('created temporary directory', tmpdirname)
            with cd(tmpdirname):
                maudBatch(CUR_DIR = os.getcwd())
                with cd("maudbatch"):
                    write_ins()
                    callMaudText.run_MAUD(
                        os.getenv('MAUD_PATH').strip("'"),
                        "mx8G",
                        'False',
                        None,
                        "fecu.ins")
                    files = [ f for f in os.listdir( os.curdir ) if os.path.isfile(f) ]
                    print(files)
                    with open('fecu.ins') as f:
                        lines = f.read()
                    print(lines)
                    assert 'FECU1010.par' in files

                # with open('FECU1010.par') as f:
                #     lines = f.readlines()
                #     for line in lines:
                #         if "" in line:
                            
                #     assert '_refine_ls_R_factor_all 0.0414889\n' in f.read()
                    
                # with open('FECU1010.par') as f:
                #     assert "_refine_ls_WSS_factor 1971.988" in f.read()

# def test_maudbatch2():
#     assert os.path.isfile('../Workshop/Tutorials/maudbatch/fecu.log')

# def test_synchrotron1():
#     assert os.path.isfile('environment_mac.yml')
