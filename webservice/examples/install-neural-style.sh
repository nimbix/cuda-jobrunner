#!/bin/bash

sudo apt-get update && sudo apt-get install -y git cmake libreadline-dev

# Install Torch
sudo mkdir -p /usr/local/torch
sudo chown -R nimbix:nimbix /usr/local/torch
curl -s https://raw.githubusercontent.com/torch/ezinstall/master/install-deps | bash
git clone https://github.com/torch/distro.git /usr/local/torch --recursive
cd /usr/local/torch/torch; echo "yes\n" | ./install.sh

. ~/.bashrc
sudo cp -r ~/.bashrc /etc/skel

# Install loadcaffe
sudo apt-get install -y libprotobuf-dev protobuf-compiler libjpeg-dev libpng12-dev
luarocks install loadcaffe
luarocks install image

# Install Neural Style
sudo mkdir -p /usr/local/neural-style
sudo chown -R nimbix:nimbix /usr/local/neural-style
cd /usr/local/neural-style
git clone https://github.com/jcjohnson/neural-style.git
cd /usr/local/neural-style/neural-style

# Download test models
/bin/bash models/download_models.sh
