#!/bin/bash

cd /beacon || exit

# Source the development virtualenv
source /env/bin/activate

# Set .gitconfig for development
/set_gitconfig.bash

export FLASK_APP='bento_beacon.app:app'

# For below command structure, see https://stackoverflow.com/questions/4437573/bash-assign-default-value

# Set default internal port to 5000
: ${INTERNAL_PORT:=5000}

# Set internal debug port, falling back to debugpy default
: ${BENTO_BEACON_DEBUGGER_INTERNAL_PORT:=5678}

python -m debugpy --listen "0.0.0.0:${BENTO_BEACON_DEBUGGER_INTERNAL_PORT}" -m flask run \
  --no-debugger \
  --no-reload \
  --host=0.0.0.0 \
  --port="${INTERNAL_PORT}"
