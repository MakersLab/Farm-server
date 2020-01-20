#!/usr/bin/env bash
if hash python3.7 2>/dev/null; then
    python3.7 -m pip install -r requirements.txt
    python3.7 install.py
else
    sh install-python.sh
    source ~/.bashrc
    python3.7 -m pip install -r requirements.txt
    python3.7 install.py
fi
