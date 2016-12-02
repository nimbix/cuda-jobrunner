#!/bin/bash

if [ -r /etc/JARVICE/jobenv.sh ]; then
    . /etc/JARVICE/jobenv.sh
fi

if [ -r /etc/JARVICE/jobinfo.sh ]; then
    . /etc/JARVICE/jobinfo.sh
fi

. /code/web/.venv/bin/activate

cd /code/web
gunicorn --bind 127.0.0.1:5000 app:app
