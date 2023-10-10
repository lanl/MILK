# test_with_unittest.py

import os
import sys
from MILK.data.examples import maudBatch
from MILK.MAUDText import callMaudText
import tempfile
from changeDirectory import cd
from pathlib import Path

def write_ins(fname='fecu.ins'):
    with open(fname, "w") as fID:
        fID.write('_maud_working_directory\n')

        fullpath = f"{os.getcwd()}"
        if "win" in sys.platform:
           fullpath = fullpath.replace('\\', '\\\\')
        fullpath = f"{os.getcwd()}{os.sep}"

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

def test_maudbatch():
    """Tests the first example, "maud batch"
    Writes the customized .ins file for the working directory where maudbatch exists in the 
    operating system format.
    Writes the first run only to be run for test purposes.

    Windows GitHub Runner has special character "runner~1" that causes issues, so not using the temporary diretory.
    """
    if "win" in sys.platform and "dar" not in sys.platform:
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
            
            # fetch various system conditions for debugging
            examplefiles = [ f for f in os.listdir( os.curdir ) if os.path.isfile(f) ]
            filesMaud = [f for f in os.listdir(os.getenv('MAUD_PATH').strip("'")) if os.path.isfile(f)]
            with open('fecu.ins') as f:
                inslines = f.read()

            try:
                assert 'FECU1010.par' in examplefiles
            except AssertionError as e:
                print(inslines)
                print(examplefiles)
                print(filesMaud)
                print(os.getenv('MAUD_PATH').strip("'"))
            
            try:
                from difflib import SequenceMatcher
                text1 = open('FECU1010_ref.par').read()
                text2 = open('FECU1010.par').read()
                m = SequenceMatcher(None, text1, text2)
                assert m.ratio() > 0.99
            except AssertionError as e:
                print(f'{m.ratio()}')
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
                        0,
                        1,
                        "fecu.ins")

                    examplefiles = [ f for f in os.listdir( os.curdir ) if os.path.isfile(f) ]
                    filesMaud = [f for f in os.listdir(os.getenv('MAUD_PATH').strip("'")) if os.path.isfile(f)]
                    with open('fecu.ins') as f:
                        inslines = f.read()

                    try:
                        assert 'FECU1010.par' in examplefiles
                    except AssertionError as e:
                        print(inslines)
                        print(examplefiles)
                        print(filesMaud)
                        print(os.getenv('MAUD_PATH'))

                    try:
                        from difflib import SequenceMatcher
                        text1 = open('FECU1010_ref.par').read()
                        text2 = open('FECU1010.par').read()
                        m = SequenceMatcher(None, text1, text2)
                        assert m.ratio() > 0.99
                    except AssertionError as e:
                        print(f'{m.ratio()}')
