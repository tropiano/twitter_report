#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install --force-reinstall -U setuptools
sudo apt-get install --reinstall python-pkg-resources

poetry install

python manage.py collectstatic --no-input
python manage.py migrate