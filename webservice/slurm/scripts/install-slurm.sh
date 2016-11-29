#!/bin/bash

SLURM_VERSION=16.05.6
SLURM_VERSION_STRING=16-05-6-1
INSTALL_ROOT=/opt

# Build and install SLURM
mkdir -p /tmp/slurm-tmp
cd /tmp/slurm-tmp
wget -o slurm-${SLURM_VERSION_STRING} https://github.com/SchedMD/slurm/archive/slurm-${SLURM_VERSION_STRING}.zip
unzip slurm-${SLURM_VERSION_STRING}.zip
cd /tmp/slurm-tmp/slurm-slurm-${SLURM_VERSION_STRING}
./configure --prefix=${INSTALL_ROOT}/slurm-${SLURM_VERSION}
make -j4
sudo make install

# Cleanup
rm -rf /tmp/slurm-tmp
