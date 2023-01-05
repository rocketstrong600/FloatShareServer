#!/bin/zsh
source .venv/bin/activate
konsole --hold -e 'python3 waitress_server.py'
