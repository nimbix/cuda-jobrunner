#!/bin/bash

sudo service supervisor start
sudo service munge start
/usr/local/scripts/generate-munge-key.sh
/usr/local/scripts/startslurm.sh
/code/rabbitmq/setup-rmq.sh

tail -f /var/supervisor.log
