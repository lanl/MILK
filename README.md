MILK
====
![](https://img.shields.io/github/languages/top/lanl/MILK)&nbsp;
![](https://img.shields.io/github/v/release/lanl/MILK)&nbsp;
![](https://img.shields.io/github/repo-size/lanl/MILK)&nbsp;
![](https://img.shields.io/github/downloads/lanl/MILK/total)&nbsp;
![](https://img.shields.io/github/contributors/lanl/MILK)&nbsp;

MAUD Interface Language Kit (MILK) is a set of Rietveld tools for automated processing of diffraction datasets. It's main features are:

* programable, custom, reproducible refinements
* database configuration of refinements
* distributed computing
* refinement summary 
* output formated for cinema_debye_scherrer 

More details can be found in documentation.

Installation and requirements
=============================

MILK requires MAUD 2.93 and python requirements are packaged in the pip install

To install:
1. install anaconda or miniconda
2. create a conda virtual environement and install the yml dependencies from github
```
conda env create -f environment.yml

```
4. install repository and dependencies from github using pip 
```
python -m pip3 install git+https://github.com/lanl/MILK.git@handle
```
2. install anaconda or miniconda
3. build the conda environment
4. install MILK in the environment


Contributing
============

Since MILK is open source we are happy about any kind of contribution. In
order suggest bug fixes, new features or improved documentation to MILK
proceed as follows:

1. fork the MILK repository to your personal GitHub account
2. clone it on your local computer
3. apply your changes
4. push your changes to your personal GitHub account
5. create a pull request to MILK/development

License
=======

C21035 MAUD Interface Tool Kit (MILK) has been acknowledged by NNSA for open source release.

© 2022. Triad National Security, LLC. All rights reserved.
This program was produced under U.S. Government contract 89233218CNA000001 for Los Alamos
National Laboratory (LANL), which is operated by Triad National Security, LLC for the U.S.
Department of Energy/National Nuclear Security Administration. All rights in the program are
reserved by Triad National Security, LLC, and the U.S. Department of Energy/National Nuclear
Security Administration. The Government is granted for itself and others acting on its behalf a
nonexclusive, paid-up, irrevocable worldwide license in this material to reproduce, prepare
derivative works, distribute copies to the public, perform publicly and display publicly, and to permit
others to do so.

