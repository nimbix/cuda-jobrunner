#!/bin/bash

if [ -r /etc/JARVICE/jobenv.sh ]; then
    . /etc/JARVICE/jobenv.sh
fi

if [ -r /etc/JARVICE/jobinfo.sh ]; then
    . /etc/JARVICE/jobinfo.sh
fi

. /code/web/.venv/bin/activate

python /code/web/app.py
