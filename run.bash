#!/bin/bash

cd /beacon || exit

if [[ -z "${INTERNAL_PORT}" ]]; then
  # Set default internal port to 5000
  INTERNAL_PORT=5000
fi

gunicorn bento_beacon.app:app \
  -w 1 \
  --threads $(( 2 * $(nproc --all) + 1)) \
  -b "0.0.0.0:${INTERNAL_PORT}"
