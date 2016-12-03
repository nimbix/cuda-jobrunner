#!/bin/bash

sudo /code/slurm/scripts/generate-munge-key.sh
sudo service munge start

sudo mkdir -p /var/log/slurm
sudo touch /var/log/slurm/accounting
sudo chown -R nimbix:nimbix /var/log/slurm
sudo mkdir -p /var/spool/slurmd

sudo service nginx start

/code/slurm/scripts/startslurm.sh
/code/rabbitmq/setup-rmq.sh


sudo service supervisor start
sudo touch /var/supervisor.log
tail -f /var/supervisor.log
