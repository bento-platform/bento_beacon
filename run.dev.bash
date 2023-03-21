#!/bin/bash

cd /beacon || exit

# Set .gitconfig for development
/set_gitconfig.bash

export FLASK_APP='bento_beacon.app:app'

# For below command structure, see https://stackoverflow.com/questions/4437573/bash-assign-default-value

# Set default internal port to 5000
: "${INTERNAL_PORT:=5000}"

# Set internal debug port, falling back to debugpy default
: "${DEBUGGER_PORT:=5683}"

python -m debugpy --listen "0.0.0.0:${DEBUGGER_PORT}" -m flask run \
  --no-debugger \
  --host=0.0.0.0 \
  --port="${INTERNAL_PORT}"
