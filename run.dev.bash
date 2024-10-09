#!/bin/bash

# The base image entrypoint takes care of setting up bento_user & running the git config script

cd /beacon || exit

# Update dependencies and install module locally
/poetry_user_install_dev.bash

export FLASK_ENV='development'
export FLASK_APP='bento_beacon.app:app'

# Set default internal port to 5000
: "${INTERNAL_PORT:=5000}"

# Set internal debug port, falling back to default in a Bento deployment
: "${DEBUGGER_PORT:=5683}"

python -m debugpy --listen "0.0.0.0:${DEBUGGER_PORT}" -m flask run \
  --no-debugger \
  --host=0.0.0.0 \
  --port="${INTERNAL_PORT}"
