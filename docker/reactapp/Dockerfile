FROM node:8.6-alpine


COPY package.json /app/package.json

WORKDIR /app
RUN npm install

COPY client /app/client
COPY config /app/config
COPY scripts /app/scripts
COPY docker /app/docker

RUN cd /app

RUN yarn install
RUN yarn build

COPY ./docker/reactapp/react-entrypoint.sh react-entrypoint.sh

RUN chmod +x react-entrypoint.sh


