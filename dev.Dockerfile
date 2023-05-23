FROM ghcr.io/bento-platform/bento_base_image:python-debian-2023.03.22

LABEL org.opencontainers.image.description="Local development image for the Bento Beacon service."
LABEL devcontainer.metadata='[{ \
  "remoteUser": "bento_user", \
  "customizations": { \
    "vscode": { \
      "extensions": ["ms-python.python", "eamodio.gitlens"], \
      "settings": {"workspaceFolder": "/beacon"} \
    } \
  } \
}]'

SHELL ["/bin/bash", "-c"]

RUN mkdir -p /beacon/config
WORKDIR /beacon

COPY requirements.txt .

RUN pip install --no-cache-dir debugpy -r requirements.txt

# Copy in run.dev.bash so that we have somewhere to start
COPY run.dev.bash .

# Use base image entrypoint to set up non-root user & drop into run.dev.bash

CMD [ "bash", "./run.dev.bash" ]
