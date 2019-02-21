#!/bin/sh

# Create dirs if necessary
echo "Creating dirs"
./scripts/create_dirs.sh

# Add cronjobs
echo "Adding cronjobs"
./setup-cronjobs.sh

# Apply database migrations
echo "Apply database migrations"
./implementation/server/manage.py migrate

# Create search index
echo "Create search index"
./implementation/server/manage.py search_index --rebuild -f &


# collect static files
echo "Collecting static files"
./implementation/server/manage.py collectstatic --no-input

# Start server
echo "Starting server"
python ./implementation/server/manage.py runserver 0.0.0.0:8000

