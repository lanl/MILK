MILK
====
![](https://img.shields.io/github/languages/top/lanl/MILK)&nbsp;
![](https://img.shields.io/github/v/release/lanl/MILK)&nbsp;
![](https://img.shields.io/github/repo-size/lanl/MILK)&nbsp;
![](https://img.shields.io/github/contributors/lanl/MILK)&nbsp;
![](https://img.shields.io/github/downloads/lanl/MILK/total)&nbsp;
[![DOI](https://zenodo.org/badge/504997628.svg)](https://zenodo.org/badge/latestdoi/504997628)


Following GitHub Action tests include:
- MAUD batch processing using MILK script
- HIPPO data 2-step analysis
- Docker container build and publishing for Linux/AMD64 arch 

| Linux | [![Python 3.9](https://github.com/lanl/MILK/actions/workflows/build_Lin39.yml/badge.svg)](https://github.com/lanl/MILK/actions/workflows/build_Lin39.yml) |
| :----------- | :----------- |
| Windows | [![Python 3.9](https://github.com/lanl/MILK/actions/workflows/build_Win39.yml/badge.svg)](https://github.com/lanl/MILK/actions/workflows/build_Win39.yml) |
| MacOS (Intel) | [![Python 3.8 - 3.10](https://github.com/lanl/MILK/actions/workflows/build_MacPy38_310.yml/badge.svg)](https://github.com/lanl/MILK/actions/workflows/build_MacPy38_310.yml) |
| Linux Docker | [![GitHub Docker](https://github.com/lanl/MILK/actions/workflows/build_docker_linux.yml/badge.svg)](https://github.com/lanl/MILK/actions/workflows/build_docker_linux.yml) |

MAUD Interface Language Kit (MILK) is a set of Rietveld tools for automated processing of diffraction datasets. It's main features are:

* programable, custom, reproducible refinements
* database configuration of refinements
* distributed computing
* refinement summary 
* output formated for cinema_debye_scherrer 

More details and tutorials can be found in the [wiki](https://github.com/lanl/MILK/wiki).

If you use the resources in this repository, please cite our [paper](https://doi.org/10.1107/S1600576723005472): 

```
Savage, D. J., Lutterotti, L., Biwer, C. M., McKerns, M., Bolme, C., Knezevic, M. & Vogel, S. C. (2023). MILK: a Python scripting interface to MAUD for automation of Rietveld analysis. J. Appl. Cryst. 56.
```

Installation and requirements
=============================

See the [MILK installation wiki](https://github.com/lanl/MILK/wiki/Installation-Overview).

Using Docker
============

If you would like to install MILK via Docker, first you would need to download and install Docker from the official website: https://www.docker.com

To build a MILK docker image, use the Dockerfile:
```
docker build -t rietveld .
```

On Linux and MacOS, to run commands and mount in a directory for MILK to write output to, use:
```
docker run -u $(id -u):$(id -g)  -v ${PWD}:/output -w /output rietveld-image milk-examples -e 1
```

On Windows, run the following command:
```
docker run -v "path\to\folder":/output -w /output rietveld milk-examples -e 1
```
The path to the folder needs to be a full absolute path for Windows.

To open the Docker container as a Virtual Machine, run:
```
docker run -v ${PWD}:/output -w /output --rm -it rietveld /bin/bash
```
`--rm` tells the container to erase additional files and directories when the container exits, essentially return the container to initial state.
`-it` tells the container to run in interactive mode, which is needed if you intend to run in bash.
`/bin/bash` tells the container to start in the bash shell. If this is not done, you can still switch to bash shell by simply typing `bash`.


NOTE: This passes in the user and group ID so files written back out match the user on the host.

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

