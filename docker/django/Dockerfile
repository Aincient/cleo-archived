FROM python:3.6
RUN apt-get update
RUN apt-get install -y python-pip python-dev build-essential libgdal-dev curl

RUN curl -sL https://deb.nodesource.com/setup_6.x | bash -
RUN apt-get install -y nodejs
RUN nodejs -v && npm -v

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt-get update && apt-get install yarn

RUN apt-get install -y cron
RUN apt-get install -y redis-tools
RUN apt-get install -y mc
RUN apt-get install -y nano
RUN apt-get install -y postgresql-client

WORKDIR /app
# Installation of application requirements
RUN pip install --upgrade pip
COPY implementation/requirements requirements
RUN pip install -r requirements/dev.txt


COPY package.json /app/package.json
RUN npm install

# Copy the app, invalidates the docker image, always copy after requirements instalation is done
COPY implementation /app/implementation
COPY docs /app/docs
COPY scripts /app/scripts
COPY src /app/src
COPY docker /app/docker

#COPY webpack-stats.json /webpack-stats.json
COPY client /app/client
COPY config /app/config


COPY setup.py /app/setup.py


RUN find . -name '*.pyc' -delete

# Frontend installation
RUN yarn install
RUN yarn build

# Setup the app for imports outside of root folder work
RUN python setup.py develop

RUN mkdir -p implementation/logs
RUN touch implementation/logs/all.log
COPY ./docker/django/django-entrypoint.sh django-entrypoint.sh
COPY ./docker/django/setup-cronjobs.sh setup-cronjobs.sh
RUN chmod +x django-entrypoint.sh
RUN chmod +x setup-cronjobs.sh

