#!/bin/sh
(crontab -l 2>/dev/null; echo "0 0 1 * * /app/scripts/reset_api_usage_counts.sh -with args") | crontab -