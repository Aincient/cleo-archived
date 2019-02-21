#!/usr/bin/env bash
cd implementation/server/
./manage.py migrate  "$@" --settings=settings.dev
