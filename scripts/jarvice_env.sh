#!/bin/bash

if [ -r /etc/JARVICE/jobinfo.sh ]; then
    . /etc/JARVICE/jobinfo.sh
fi

if [ -r /etc/JARVICE/jobenv.sh ]; then
    . /etc/JARVICE/jobenv.sh
fi

if [ -r /code/web/.venv/bin/activate ]; then
    . /code/web/.venv/bin/activate
fi

exec $@
