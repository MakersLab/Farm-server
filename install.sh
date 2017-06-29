#!/usr/bin/env bash
if hash python3.6 2>/dev/null; then
    python3.6 -m pip install -r requirements.txt
    python3.6 install.py
else
    sh install-python.sh
    source ~/.bashrc
    python3.6 -m pip install -r requirements.txt
    python3.6 install.py
fi
