#!/usr/bin/env bash
cd implementation/server/
./manage.py search_index --populate -f --settings=settings.dev
