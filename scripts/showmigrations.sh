#!/usr/bin/env bash
cd implementation/server/
./manage.py showmigrations "$@" --settings=settings.dev
