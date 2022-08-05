#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 20:22:15 2021

@author: danielsavage
"""

import os
import shutil
from urllib import request
import zipfile


def qpa(path='QPA'):
    """Download the qauntitative phase analysis example from MAUD website."""
    url = "http://nanoair.dii.unitn.it:8080/static/tutorial/alzrc.zip"
    dpath = download_example(url, path, os.path.basename(url))
    unzip_download(dpath, path)


def maudbatch(path='Maudbatch'):
    """Download the Maudbatch phase analysis example from MAUD website."""
    url = "http://nanoair.dii.unitn.it:8080/static/tutorial/batch.zip"
    dpath = download_example(url, path, os.path.basename(url))
    unzip_download(dpath, path)


def hippo_texture(path='HIPPO/texture'):
    """HIPPO two phase texture example."""
    fn = os.path.join(os.path.dirname(__file__), '../../examples/HIPPO/texture')
    shutil.copytree(fn, os.path.join(os.getcwd(), path))


def sequential_refinement(path='synchrotron/sequential_refinement'):
    """Synchrotron three sequential refinement example."""
    fn = os.path.join(os.path.dirname(__file__), '../../examples/synchrotron/sequential_refinement')
    shutil.copytree(fn, os.path.join(os.getcwd(), path))


def download_example(url, path, filename):
    """
    Download URL and return path to download.

    Parameters
    ----------
    url : str
        Valid http:///.. url.
    path : Path relative to the working directory to put the data
        DESCRIPTION.
    filename : str.
        Name for downloaded file
    Returns
    -------
    download_path : str.
        Full path to download.

    """
    os.makedirs(path, exist_ok=True)
    download_path = os.path.join(os.getcwd(), path, filename)
    request.urlretrieve(url, download_path)
    return download_path


def unzip_download(download_path, export_path):
    """Extract all contents of zip."""
    with zipfile.ZipFile(download_path, 'r') as zobj:
        zobj.extractall(path=export_path)
