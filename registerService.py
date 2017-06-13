#!/usr/bin/env python3.5
import os

USER = 'pi'
WORKING_DIRECTORY = os.path.join((os.path.dirname(os.path.realpath(__file__))),'server','')
EXEC_START = os.path.join((os.path.dirname(os.path.realpath(__file__))),'server', 'main.py')

FILENAME = 'farm.service'

def main():
    with open(FILENAME, 'r') as f:
        serviceTemplate = f.read()
        f.close()
    serviceFile = serviceTemplate.format(user=USER, workingDirectory=WORKING_DIRECTORY, execStart=EXEC_START)
    print('Creating/overwriting service file')
    with open('/etc/systemd/system/'+FILENAME, 'w') as f:
        f.write(serviceFile)
        f.close()
    print('Done creating service file')
    os.system('systemctl daemon-reload')
    os.system('chmod 771 server/main.py')
    os.system('service farm start')

if __name__ == '__main__':
    main()