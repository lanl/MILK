# test_with_unittest.py

import os

def test_maudbatch1():
    assert os.path.isfile('../Workshop/Tutorials/maudbatch/FECU1010.par')

def test_maudbatch2():
    assert os.path.isfile('../Workshop/Tutorials/maudbatch/fecu.log')

# def test_synchrotron1():
#     assert os.path.isfile('environment_mac.yml')