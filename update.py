#!/usr/bin/env python3.7
import downloadBuild
import os

def main():
    os.system('service farm stop')
    os.system('git pull')
    os.system('python3.7 -m pip install -r requirements.txt')
    os.system('chmod 771 server/main.py')
    downloadBuild.main()
    os.system('service farm start')

if __name__ == '__main__':
    main()