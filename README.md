MILK
====
![](https://img.shields.io/github/languages/top/lanl/MILK)&nbsp;
![](https://img.shields.io/github/v/release/lanl/MILK)&nbsp;
![](https://img.shields.io/github/repo-size/lanl/MILK)&nbsp;
![](https://img.shields.io/github/contributors/lanl/MILK)&nbsp;

MAUD Interface Language Kit (MILK) is a set of Rietveld tools for automated processing of diffraction datasets. It's main features are:

* programable, custom, reproducible refinements
* database configuration of refinements
* distributed computing
* refinement summary 
* output formated for cinema_debye_scherrer 

More details and tutorials can be found in the [wiki](https://github.com/lanl/MILK/wiki).

Installation and requirements
=============================

MILK requires the most recent MAUD release which is currently hosted in the Dropbox MAUD folder. Python requirements are packaged in the conda environement.yml.

To install:
1. install anaconda or miniconda
2. Clone the MILK repository locally.

```bash
git clone https://github.com/lanl/MILK.git
```

You may need to configure your git proxy for the clone to work
```
git config --global http.proxy http://myproxy:port
```

3. To install MILK locally in terminal navigate to the repository and run
```bash
conda env create -f environment.yml
```
By editing environment.yml, the name of the conda environment can be changed from the default "rietveld" to e.g. "rietveld_test" or so. For the install to complete you may need to configure your conda and your git proxy e.g. 
```
conda config --set proxy_servers.http http://myproxy:port
conda config --set proxy_servers.https https://myproxy:port
git config --global http.proxy http://myproxy:port
python -m pip config set global.proxy http://myproxy:port
```

4. To install your MAUD path and CINEMA to your conda environment run
```bash
config_maud.py /path/to/maud/application/Maud.app -c /path/to/cinema/repo
```
MILK uses the bash key $MAUD_PATH and $CINEMA_PATH unless a path is specified in the milk.json file.

In the case you are on linux or windows, you just specify the Maud folder without the .app

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

