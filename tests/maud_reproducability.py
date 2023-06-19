# test_with_unittest.py

import os
import sys
from MILK.data.examples import maudBatch
from MILK.MAUDText import callMaudText
import tempfile
from changeDirectory import cd
from workshop_examples import write_ins

def test_maudbatch2():
    """Tests the first example, "maud batch"
    Writes the customized .ins file for the working directory where maudbatch exists in the 
    operating system format.
    Writes the first run only to be run for test purposes.
    """
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
                assert os.path.isfile('FECU1010.par')

                with open('FECU1010.par') as f:
                    lines = f.readlines()
                    for line in lines:
                        assert '_refine_ls_R_factor_all 0.04141889' in line
                    for line in lines:
                        assert '_refine_ls_WSS_factor 1971.4988' in line

# def test_maudbatch2():
#     assert os.path.isfile('../Workshop/Tutorials/maudbatch/fecu.log')

# def test_synchrotron1():
#     assert os.path.isfile('environment_mac.yml')