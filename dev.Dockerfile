# ARG BASE_IMAGE
# ARG BASE_IMAGE_VERSION

# debian image
# FROM python:3.8-slim-bullseye
FROM ghcr.io/bento-platform/bento_base_image:python-debian-latest

WORKDIR /beacon

COPY ./entrypoint.dev.sh ./requirements.txt /beacon/bento_beacon/

# shared volume with local repo, see docker.compose.dev.yaml
WORKDIR /beacon/bento_beacon

RUN pip install debugpy -r requirements.txt; 

CMD [ "sh", "./entrypoint.dev.sh" ]
