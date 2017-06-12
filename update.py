#!/usr/bin/env python3.5
import downloadBuild
import os

def main():
    os.system('git pull')
    downloadBuild.main()

if __name__ == '__main__':
    main()