#!/bin/bash

cd /beacon || exit

# Source the development virtualenv
source /env/bin/activate

# Set .gitconfig for development
/set_gitconfig.bash

export FLASK_APP='bento_beacon.app:app'

if [[ -z "${INTERNAL_PORT}" ]]; then
  # Set default internal port to 5000
  INTERNAL_PORT=5000
fi

python -m debugpy --wait-for-client --listen 0.0.0.0:5678 -m flask run \
  --no-debugger \
  --no-reload \
  --host=0.0.0.0 \
  --port="${INTERNAL_PORT}"
