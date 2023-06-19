#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 20:22:15 2021

@author: danielsavage
"""

import os
from pathlib import Path
import shutil
from urllib import request
import zipfile

MOD_DIR = Path(__file__).parent

# def qpa(path='QPA'):
#     """Download the qauntitative phase analysis example from MAUD website."""
#     url = "http://nanoair.dii.unitn.it:8080/static/tutorial/alzrc.zip"
#     dpath = download_example(url, path, os.path.basename(url))
#     unzip_download(dpath, path)


def maudBatch(CUR_DIR = Path().cwd(),path='maudbatch'):
    """MAUD batch analysis example updated for newer versions of MAUD."""
    # url = "http://nanoair.dii.unitn.it:8080/static/tutorial/batch.zip"
    # dpath = download_example(url, path, os.path.basename(url))
    # unzip_download(dpath, path)
    fout = Path(CUR_DIR) / path
    fin = MOD_DIR / '../../examples/maudbatch'
    shutil.copytree(fin, fout)
    shutil.copy(MOD_DIR / '../../examples/data/MAUD_batch.zip', fout)
    unzip(fout / 'MAUD_batch.zip', fout)

def hippoTexture(CUR_DIR = Path().cwd(),path='HIPPO/texture'):
    """HIPPO two phase texture example."""
    fout = Path(CUR_DIR) / path
    fin = MOD_DIR / '../../examples/HIPPO/texture'
    shutil.copytree(fin, fout)
    shutil.copy(MOD_DIR / '../../examples/data/HIPPO_texture.zip', fout)
    unzip(fout / 'HIPPO_texture.zip', fout)
    shutil.move(fout / 'HIPPO_texture', fout / 'data')

def sequentialRefinement(CUR_DIR = Path().cwd(),path='sequential_refinement'):
    """Synchrotron three sequential refinement example."""
    fout = Path(CUR_DIR) / path
    shutil.copytree(
        MOD_DIR / '../../examples/Synchrotron/sequential_refinement', fout)
    shutil.copy(MOD_DIR / '../../examples/data/CHESS_insitu.zip', fout)
    unzip(fout / 'CHESS_insitu.zip', fout)
    shutil.move(fout / 'CHESS_insitu', fout / 'data')


def GEDetector(CUR_DIR = Path().cwd(),path='CHESS-GE'):
    """CHESS: GE Detector calibration and integration example."""
    fout = Path(CUR_DIR) / path
    fin = MOD_DIR / '../../examples/Detector_Calibrations/CHESS-GE'
    shutil.copytree(fin, fout)
    unzip(fout / 'Archive.zip', fout)


def APSHydra(CUR_DIR = Path().cwd(),path='APS-1ID-Hydra'):
    """CHESS: GE Detector calibration and integration example."""
    fout = Path(CUR_DIR) / path
    fin = MOD_DIR / '../../examples/Detector_Calibrations/APS-1ID-Hydra'
    shutil.copytree(fin, fout)
    unzip(fout / 'Archive.zip', fout)


def SLACMEC(CUR_DIR = Path().cwd(),path='SLAC-MEC'):
    """CHESS: GE Detector calibration and integration example."""
    fout = Path(CUR_DIR) / path
    fin = MOD_DIR / '../../examples/Detector_Calibrations/SLAC-MEC'
    shutil.copytree(fin, fout)
    unzip(fout / 'Archive.zip', fout)


def euXFEL(CUR_DIR = Path().cwd(),path='euXFEL-HED'):
    """CHESS: GE Detector calibration and integration example."""
    fout = Path(CUR_DIR) / path
    fin = MOD_DIR / '../../examples/Detector_Calibrations/euXFEL-HED'
    shutil.copytree(fin, fout)
    unzip(fout / 'Archive.zip', fout)


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


def unzip(input, export_path, remove_zip=True):
    """Extract all contents of zip."""
    with zipfile.ZipFile(input, 'r') as zobj:
        zobj.extractall(path=export_path)
    os.remove(input)