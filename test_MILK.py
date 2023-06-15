# test_with_unittest.py

import os

def test_maudbatch():
    for dirpath, dirnames, filenames in os.walk("."):
        for filename in [f for f in filenames if f.endswith(".log")]:
            print os.path.join(dirpath, filename)
    assert os.path.isfile('/Tutorials/maudbatch/environment.yml')

def test_always_fails():
    assert os.path.isfile('environment_mac.yml')