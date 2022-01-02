#!/bin/bash

rm -rf input output
mkdir input output
nohup venv/bin/python -u websocket.py & >/dev/null
