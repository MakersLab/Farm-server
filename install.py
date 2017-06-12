#!/usr/bin/env python3.5
import downloadBuild
import registerService

def main():
    registerService.main()
    downloadBuild.main()
    

if __name__ == '__main__':
    main()