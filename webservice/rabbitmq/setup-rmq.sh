#!/bin/bash

127  sudo rabbitmqctl add_user nimbix nimbix
128  sudo rabbitmqctl list_users
129  sudo rabbitmqctl set_user_tags nimbix administrator
130  ls
131  sudo tail -f /var/log/rabbitmq/rabbit\@*.log
132  rabbitmqctl set_permissions -p / nimbix ".*" ".*" ".*"
