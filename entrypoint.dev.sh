#!/bin/sh
cd ./bento_beacon/
python -m debugpy --wait-for-client --listen 0.0.0.0:5678 -m flask run --no-debugger --host=0.0.0.0 --port=5000