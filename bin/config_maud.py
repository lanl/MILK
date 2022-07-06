#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 11:11:33 2022

@author: danielsavage
"""
import zipfile
import os
import shutil
import sys
import subprocess
import tarfile
import gzip
from urllib import request


conda_prefix = os.getenv('CONDA_PREFIX')

maud_prefix = os.path.join(conda_prefix, 'maud')
if os.path.exists(maud_prefix):
    shutil.rmtree(maud_prefix)
os.makedirs(maud_prefix)


# with zipfile.ZipFile(maud_download, 'r') as zip_ref:
#     zip_ref.extractall(maud_prefix)


# tar = tarfile.open(maud_download, "r:gz")
# tar.extractall()
# tar.close()


def gunzip(source_filepath, dest_filepath, block_size=65536):
    with gzip.open(source_filepath, 'rb') as s_file, \
            open(dest_filepath, 'wb') as d_file:
        while True:
            block = s_file.read(block_size)
            if not block:
                break
            else:
                d_file.write(block)


def mac_install(maud_prefix):
    url = "http://nanoair.dii.unitn.it:8080/static/macosx64/Maud.dmg.gz"
    maud_download = os.path.join(maud_prefix, os.path.basename(url))
    get_url(url, maud_download)
    maud_dmg = os.path.join(maud_prefix, 'maud.dmg')
    gunzip(maud_download, maud_dmg)
    subprocess.call(["hdiutil", "attach", maud_dmg])
    subprocess.call(["cp", "-R", "/Volumes/maud/Maud.app", maud_prefix])
    subprocess.call(["hdiutil", "unmount", "/Volumes/maud/Maud.app"])
    subprocess.call(["rm", maud_dmg])
    subprocess.call(["rm", maud_download])
    env_act = os.path.join(conda_prefix, "etc/conda/activate.d")
    subprocess.call(["mkdir", "-p", env_act])
    env_act_post = os.path.join(env_act, "post.sh")
    f = open(env_act_post, "w")
    subprocess.call(
        "echo export PATH=${PATH}:${CONDA_PREFIX}/maud/Maud.app/Contents/MacOS".split(), stdout=f)
    f.close()


def get_url(url, maud_download):
    request.urlretrieve(url, maud_download)


if __name__ == "main":
    if "linux" in sys.platform:
        # linux
        url = "http://nanoair.dii.unitn.it:8080/static/linux64_openjdk/Maud.tar.gz"
    elif "darwin" in sys.platform:
        # OS X
        mac_install(maud_prefix)
    elif "win" in sys.platform:
        # Windows...
        url = "http://nanoair.dii.unitn.it:8080/static/windows64_openjdk/Maud.zip"
    else:
        raise OSError("Unsupported OS for automated MAUD installation")
