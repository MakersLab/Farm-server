#!/usr/bin/env bash

cd server
python3 printerState.py > logs/printerState.txt &
python3 websocket.py > logs/websocket.txt &
python3 server.py > logs/server.txt &
