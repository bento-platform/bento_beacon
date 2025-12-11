FROM ghcr.io/bento-platform/bento_base_image:python-debian-2025.12.01

SHELL ["/bin/bash", "-c"]

RUN mkdir -p /beacon/config
WORKDIR /beacon

# Install dependencies
COPY pyproject.toml .
COPY poetry.lock .
RUN pip install --no-cache-dir gunicorn==23.0.0 && \
    poetry config virtualenvs.create false && \
    poetry install --without dev --no-root

# Copy whole project directory
COPY . .

# Install the module itself, locally (similar to `pip install -e .`)
RUN poetry install --without dev

# Use base image entrypoint to set up non-root user & drop into run.bash

CMD [ "bash", "./run.bash" ]
