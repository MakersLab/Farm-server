#!/usr/bin/env bash
if hash python3.7 2>/dev/null; then
    echo python3.7 is alredy installed
else
    apt-get -y install libbz2-dev liblzma-dev libsqlite3-dev libncurses5-dev libgdbm-dev zlib1g-dev libreadline-dev libssl-dev tk-dev build-essential libncursesw5-dev libc6-dev openssl
    mkdir python3.7
    wget https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tgz
    tar xzvf Python-3.6.1.tgz
    cd Python-3.6.1/
    ./configure
    make
    make install
fi