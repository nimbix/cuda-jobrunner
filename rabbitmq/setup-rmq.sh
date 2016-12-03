#!/bin/bash

sudo service rabbitmq-server start
sudo rabbitmqctl add_user nimbix nimbix
sudo rabbitmqctl set_user_tags nimbix administrator
sudo rabbitmqctl set_permissions -p / nimbix ".*" ".*" ".*"
sudo rabbitmq-plugins enable rabbitmq_management
