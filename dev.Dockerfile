FROM ghcr.io/bento-platform/bento_base_image:python-debian-2024.10.01

LABEL org.opencontainers.image.description="Local development image for the Bento Beacon service."
LABEL devcontainer.metadata='[{ \
  "remoteUser": "bento_user", \
  "customizations": { \
    "vscode": { \
      "extensions": ["ms-python.python", "eamodio.gitlens", "ms-python.black-formatter"], \
      "settings": { \
        "workspaceFolder": "/beacon", \
        "[python]": { \
          "editor.defaultFormatter": "ms-python.black-formatter", \
          "black-formatter.args": ["--line-length", "120"] \
        } \
      } \
    } \
  } \
}]'

SHELL ["/bin/bash", "-c"]

WORKDIR /beacon

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

# Install production + development dependencies
# Without --no-root, we get errors related to the code not being copied in yet.
# But we don't want the code here, otherwise Docker cache doesn't work well.
RUN poetry config virtualenvs.create false && \
    poetry install --no-root

# Copy in run.dev.bash so that we have somewhere to start
COPY run.dev.bash .

# Tell the service that we're running a local development container
ENV BENTO_CONTAINER_LOCAL=true

# Don't copy any code in - the dev compose file will mount the repo
# Use base image entrypoint to set up non-root user & drop into run.dev.bash

CMD [ "bash", "./run.dev.bash" ]
