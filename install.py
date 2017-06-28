#!/usr/bin/env python3.6
import downloadBuild
import registerService
import os

def main():
    os.system('python3.6 -m pip install -r requirements.txt')
    registerService.main()
    downloadBuild.main()
    os.makedirs('./server/data')
    

if __name__ == '__main__':
    main()