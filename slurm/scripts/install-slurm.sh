#!/bin/bash

SLURM_VERSION=16.05.6
SLURM_VERSION_STRING=16-05-6-1
INSTALL_ROOT=/opt

sudo apt-get install -y libmysqlclient-dev

# Build and install SLURM
mkdir -p /tmp/slurm-tmp
cd /tmp/slurm-tmp
wget -o slurm-${SLURM_VERSION_STRING} https://github.com/SchedMD/slurm/archive/slurm-${SLURM_VERSION_STRING}.zip
unzip slurm-${SLURM_VERSION_STRING}.zip
cd /tmp/slurm-tmp/slurm-slurm-${SLURM_VERSION_STRING}
./configure --prefix=${INSTALL_ROOT}/slurm-${SLURM_VERSION}
make -j4
sudo make install
sudo ln -sf /opt/slurm-${SLURM_VERSION} /opt/slurm

sudo mkdir -p /var/spool/slurm /var/pool/slurmd
sudo mkdir -p /var/log/slurm
sudo touch /var/log/slurm/accounting
sudo chown -R nimbix:nimbix /var/spool/slurm /var/log/lsurm

# Cleanup
rm -rf /tmp/slurm-tmp
