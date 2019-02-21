#!/bin/sh
echo "Reseting api usage counts"
./implementation/server/manage.py muses_reset_api_usage_counts --group=authenticated_user