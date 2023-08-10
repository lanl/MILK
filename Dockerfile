# License

# C21035 MAUD Interface Tool Kit (MILK) has been acknowledged by NNSA for open source release.

# © 2022. Triad National Security, LLC. All rights reserved. This program was produced under 
# U.S. Government contract 89233218CNA000001 for Los Alamos National Laboratory (LANL), which 
# is operated by Triad National Security, LLC for the U.S. Department of Energy/National Nuclear 
# Security Administration. All rights in the program are reserved by Triad National Security, LLC, 
# and the U.S. Department of Energy/National Nuclear Security Administration. The Government is 
# granted for itself and others acting on its behalf a nonexclusive, paid-up, irrevocable worldwide 
# license in this material to reproduce, prepare derivative works, distribute copies to the public, 
# perform publicly and display publicly, and to permit others to do so.

FROM mambaorg/micromamba:1.4.9

# environment variables
ENV MAUD_PATH=/Maud
ENV CINEMA_PATH=/cinema
ENV HOME=/home/$MAMBA_USER

# assign folder ownership to mamba
COPY --chown=$MAMBA_USER:$MAMBA_USER . $HOME/
WORKDIR $HOME

# Install MILK
RUN micromamba install -v -y -n base -f "${HOME}/environments/environment_linux_docker.yml" && \
    echo "conda activate $CONDA_ENV" >> ~/.bashrc

USER root

RUN apt-get update && apt-get install -y wget && apt-get install -y git

# Install MAUD
RUN wget -O Maud.tar.gz https://www.dropbox.com/sh/3l4jpjw7mkc3cfo/AABxmzMfRS2zsxfXhUNftZHCa/linux64/Maud.tar.gz?dl=1 \
    && tar -xvzf Maud.tar.gz

# Install Cinema
RUN mkdir -p ${CINEMA_PATH} && \
    git clone https://github.com/cinemascience/cinema_debye_scherrer.git ${CINEMA_PATH} && \
    chown $MAMBA_USER:$MAMBA_USER ${CINEMA_PATH}

RUN echo '[ ! -z "$TERM" -a -r /etc/motd ] && cat /etc/issue && cat /etc/motd' \
    >> /etc/bash.bashrc \
    ; echo "\
    License \n \
    \n \
    C21035 MAUD Interface Tool Kit (MILK) has been acknowledged by NNSA for open source release. \n\
    © 2022. Triad National Security, LLC. All rights reserved. This program was produced under \n\
    U.S. Government contract 89233218CNA000001 for Los Alamos National Laboratory (LANL), which \n\
    is operated by Triad National Security, LLC for the U.S. Department of Energy/National Nuclear \n\
    Security Administration. All rights in the program are reserved by Triad National Security, LLC, \n\
    and the U.S. Department of Energy/National Nuclear Security Administration. The Government is \n\
    granted for itself and others acting on its behalf a nonexclusive, paid-up, irrevocable worldwide\n\ 
    license in this material to reproduce, prepare derivative works, distribute copies to the public, \n\
    perform publicly and display publicly, and to permit others to do so.\n"\
    > /etc/motd
