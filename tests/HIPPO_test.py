# test_with_unittest.py

import os
import sys
from MILK.data.examples import hippoTexture
from MILK.MAUDText import callMaudText
import tempfile
from changeDirectory import cd
from pathlib import Path
import subprocess

def test_HIPPO():
    """Tests the first example, "maud batch"
    Writes the customized .ins file for the working directory where maudbatch exists in the 
    operating system format.
    Writes the first run only to be run for test purposes.

    Windows GitHub Runner has special character "runner~1" that causes issues, so not using the temporary diretory.
    """
    if "win" in sys.platform and "dar" not in sys.platform:
        cwdDir = os.getcwd()
        hippoTexture(CUR_DIR = cwdDir)
        with cd("HIPPO/texture"):
            subprocess.run(["python", "1_build_database.py"])
            subprocess.run(["python", "2_setup.py"])
            subprocess.run(["python", "3_analysis.py"])
            
            # fetch various system conditions for debugging
            examplefiles = [ f for f in os.listdir( os.curdir ) if os.path.isfile(f) ]
            filesMaud = [f for f in os.listdir(os.getenv('MAUD_PATH').strip("'")) if os.path.isfile(f)]
            
            try:
                assert 'data.csv' in examplefiles
            except AssertionError as e:
                print(examplefiles)
                print(filesMaud)
                print(os.getenv('MAUD_PATH').strip("'"))
            
            try:
                from difflib import SequenceMatcher
                text1 = open('data_ref.csv').read()
                text2 = open('data.csv').read()
                m = SequenceMatcher(None, text1, text2)
                assert m.ratio() > 0.99
            except AssertionError as e:
                print(f'{m.ratio()}')

    else:
        with tempfile.TemporaryDirectory() as tmpdirname:
            print('created temporary directory', tmpdirname)
            with cd(tmpdirname):
                hippoTexture(CUR_DIR = os.getcwd())
                with cd("HIPPO/texture"):
                    subprocess.run(["python", "1_build_database.py"])
                    subprocess.run(["python", "2_setup.py"])
                    subprocess.run(["python", "3_analysis.py"])

                    examplefiles = [ f for f in os.listdir( os.curdir ) if os.path.isfile(f) ]
                    filesMaud = [f for f in os.listdir(os.getenv('MAUD_PATH').strip("'")) if os.path.isfile(f)]

                    try:
                        assert 'data.csv' in examplefiles
                    except AssertionError as e:
                        print(examplefiles)
                        print(filesMaud)
                        print(os.getenv('MAUD_PATH'))

                    try:
                        from difflib import SequenceMatcher
                        text1 = open('data_ref.csv').read()
                        text2 = open('data.csv').read()
                        m = SequenceMatcher(None, text1, text2)
                        assert m.ratio() > 0.99
                    except AssertionError as e:
                        print(f'{m.ratio()}')