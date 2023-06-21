ARG CONDA_VERSION=23.3.1-0
FROM continuumio/miniconda3:${CONDA_VERSION} as build

ARG CONDA_ENV=milk

ENV MAUD_PATH=/Maud
ENV CINEMA_PATH=/cinema
ENV PATH="${PATH}:/opt/conda/envs/${CONDA_ENV}/bin"

# Fetch MILK
COPY . /MILK

# Pre-requisites
ENV DEBIAN_FRONTEND noninteractive
RUN apt update \
    && apt -y install \
        vim \
    && rm -rf /var/lib/apt/lists/*

# Install MILK
RUN cd MILK \
    && conda install mamba -n base -c conda-forge \
    && mamba create -n ${CONDA_ENV} -c conda-forge openmpi mpi4py \
    && mamba env update -n ${CONDA_ENV} -f environment_linux.yml \
    && echo "conda activate $CONDA_ENV" >> ~/.bashrc

# Install MAUD
RUN wget -O Maud.tar.gz https://www.dropbox.com/sh/3l4jpjw7mkc3cfo/AABxmzMfRS2zsxfXhUNftZHCa/linux64/Maud.tar.gz?dl=0 \
    && tar -xvzf Maud.tar.gz

# Install Cinema
RUN mkdir -p ${CINEMA_PATH} \
    && git clone https://github.com/cinemascience/cinema_debye_scherrer.git ${CINEMA_PATH}
