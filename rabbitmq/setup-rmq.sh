#!/bin/bash

sudo rabbitmqctl add_user nimbix nimbix
sudo rabbitmqctl set_user_tags nimbix administrator
sudo rabbitmqctl set_permissions -p / nimbix ".*" ".*" ".*"
sudo service rabbitmq-server start
