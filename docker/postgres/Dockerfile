FROM mdillon/postgis

RUN apt-get update -y

RUN mkdir -p /docker-entrypoint-initdb.d
COPY ./docker/postgres/posgis-init-entry.sh /docker-entrypoint-initdb.d/posgis-init-entry.sh