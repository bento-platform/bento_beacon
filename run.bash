#!/bin/bash

cd /beacon || exit

export FLASK_APP='bento_beacon.app:app'

# Set default internal port to 5000
: "${INTERNAL_PORT:=5000}"

python -m gunicorn "${FLASK_APP}" \
  -w 1 \
  --threads $(( 2 * $(nproc --all) + 1)) \
  -b "0.0.0.0:${INTERNAL_PORT}"
