#!/bin/sh
python -m debugpy --wait-for-client --listen 0.0.0.0:5678 -m flask run --no-debugger --no-reload --host=0.0.0.0:5000
