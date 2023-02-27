FROM ghcr.io/bento-platform/bento_base_image:python-debian-latest

SHELL ["/bin/bash", "-c"]

WORKDIR /beacon

COPY requirements.txt .

RUN source /env/bin/activate && pip install debugpy -r requirements.txt

# Use base image entrypoint to set up non-root user & drop into run.dev.bash

CMD [ "bash", "./run.dev.bash" ]
