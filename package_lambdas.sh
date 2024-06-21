#!/bin/bash

deactivate
rm -rf lambdas/.venv
python3 -m venv lambdas/.venv
source lambdas/.venv/bin/activate
pip install -r lambda-requirements.txt
deactivate
rm -rf lambdas/.venv/lib/python*/site-packages/_distutils*
rm -rf lambdas/.venv/lib/python*/site-packages/distutils*
rm -rf lambdas/.venv/lib/python*/site-packages/pip*
rm -rf lambdas/.venv/lib/python*/site-packages/pkg_resources
rm -rf lambdas/.venv/lib/python*/site-packages/setuptools*
rm -rf lambdas/.venv/lib/python*/site-packages/__pycache__
cp -a lambdas/.venv/lib/python*/site-packages/* lambdas/
rm -rf lambdas/.venv
