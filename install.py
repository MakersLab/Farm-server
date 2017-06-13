#!/usr/bin/env python3.5
import downloadBuild
import registerService
import os

def main():
    os.system('python3.5 -m pip install -r requirements.txt')
    registerService.main()
    downloadBuild.main()
    

if __name__ == '__main__':
    main()