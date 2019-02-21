#!/usr/bin/env bash
pip install -r implementation/requirements/dev.txt
python setup.py develop
./scripts/create_dirs.sh
python implementation/server/manage.py collectstatic --noinput
python implementation/server/manage.py migrate --noinput
