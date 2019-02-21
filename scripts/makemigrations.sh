#!/usr/bin/env bash
cd implementation/server/
./manage.py makemigrations "$@" --settings=settings.dev
