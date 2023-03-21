FROM ghcr.io/bento-platform/bento_base_image:python-debian-2023.03.06

LABEL org.opencontainers.image.description="Local development image for the Bento Beacon service."
LABEL devcontainer.metadata='[{ \
  "remoteUser": "bento_user", \
  "customizations": { \
    "vscode": { \
      "extensions": ["ms-python.python"], \
      "settings": {"workspaceFolder": "/beacon"} \
    } \
  }, \
  "workspaceFolder": "/beacon" \
}]'

SHELL ["/bin/bash", "-c"]

WORKDIR /beacon

COPY requirements.txt .

RUN pip install debugpy -r requirements.txt

# Copy in run.dev.bash so that we have somewhere to start
COPY run.dev.bash .

# Use base image entrypoint to set up non-root user & drop into run.dev.bash

CMD [ "bash", "./run.dev.bash" ]
