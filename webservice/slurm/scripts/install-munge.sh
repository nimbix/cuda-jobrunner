#!/bin/bash

sudo apt-get update
sudo apt-get install -y --force-yes libbz2-dev libssl-dev autoconf build-essential curl wget unzip munge libmunge2 libmunge-dev

# Build and install Munge
# mkdir -p /tmp/munge-tmp
# cd /tmp/munge-tmp
# curl -L -o munge-${MUNGE_VER}.zip https://github.com/dun/munge/archive/munge-${MUNGE_VER}.zip
# unzip munge-${MUNGE_VER}.zip && mv munge-munge-${MUNGE_VER} munge-${MUNGE_VER}
# tar cjf munge-${MUNGE_VER}.tar.bz2 munge-${MUNGE_VER}
# cd /tmp/munge-tmp/munge-${MUNGE_VER}
# ./configure --prefix=/opt/munge-${MUNGE_VER}
# make -j4
# sudo make install
# rm -rf /tmp/munge-tmp
sudo rm -rf /var/lib/apt/*
