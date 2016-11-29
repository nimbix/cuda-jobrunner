#!/bin/bash

cd `dirname $0`
VENV_DIR=`dirname $0`/.venv
virtualenv  ${VENV_DIR}

echo "Virtualenv is: ${VENV_DIR}"
/bin/bash -c ". ${VENV_DIR}/bin/activate; echo `which pip`"
/bin/bash -c ". ${VENV_DIR}/bin/activate; pip install -r requirements.txt"
