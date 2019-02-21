#!/bin/sh

createdb -T template0 -E utf-8 -l en_US.UTF-8 -O postgres muses
psql  -c 'create extension postgis;' -d muses