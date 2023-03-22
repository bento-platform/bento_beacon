FROM ghcr.io/bento-platform/bento_base_image:python-debian-2023.03.22

SHELL ["/bin/bash", "-c"]

RUN mkdir -p /beacon/config
WORKDIR /beacon

# Install dependencies
COPY requirements.txt .
RUN pip install "gunicorn==20.1.0" -r requirements.txt

# Copy whole project directory
COPY . .

# Use base image entrypoint to set up non-root user & drop into run.bash

CMD [ "bash", "./run.bash" ]
