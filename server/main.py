#!/usr/bin/env python3.5
from multiprocessing import Process
import time
import os

from printerState import main as printerStateMain
from server import main as serverMain
from websocket import main as websocketServerMain

servicesTemplate = {
    'server': {
        'name': 'Server',
        'run': serverMain,
        'running': False
    },
    'printerState': {
        'name': 'Printer State',
        'run': printerStateMain,
        'running': False
    },
    'websocketServer': {
        'name': 'Websocket server',
        'run': websocketServerMain,
        'running': False
    }
}


class ServiceManager:
    def __init__(self, services, autoStart=False):
        self.log('Creating processes')
        self.services = services
        for serviceName in services:
            newProcess = Process(target=self.services[serviceName]['run'])
            newProcess.daemon = True
            self.services[serviceName]['process'] = newProcess
            if (autoStart):
                newProcess.start()
                self.log('Creating and starting process for {0} with pid {1}'.format(self.services[serviceName]['name'], newProcess.pid))
                self.services[serviceName]['running'] = True
            else:
                self.log('Creating process for {0}'.format(self.services[serviceName]['name']))
                self.services[serviceName]['running'] = False

    def updateServiceState(self):
        servicesRunning = []
        servicesStopped = []
        for serviceName in self.services:
            self.services[serviceName]['running'] = self.services[serviceName]['process'].is_alive()
            if(self.services[serviceName]['running']):
                servicesRunning.append(self.services[serviceName]['name'])
            else:
                servicesStopped.append(self.services[serviceName]['name'])
        if(len(servicesStopped) != 0):
            self.log('Services stopped: {0}'.format(','.join(servicesStopped)))

    def restartStoppedServices(self):
        for serviceName in self.services:
            if (not self.services[serviceName]['running']):
                self.startService(serviceName)

    def startService(self, serviceName):
        if(self.services[serviceName]['running']):
            self.log('Cant start service which is already running', 'warning')
        else:
            self.services[serviceName]['process'].terminate()
            self.services[serviceName]['process'] = Process(target=self.services[serviceName]['run'])
            self.services[serviceName]['process'].start()
            self.log('Creating and starting process for {0} with pid {1}'.format(
                self.services[serviceName]['name'],
                self.services[serviceName]['process'].pid))
            self.services[serviceName]['running'] = True

    def loop(self):
        while True:
            self.updateServiceState()
            self.restartStoppedServices()
            time.sleep(4)

    def log(self, message, level='info'):
        print('{0}-[Service Manager][{2}] {1}'.format(round(time.time()), message, level))

def main():
    services = ServiceManager(servicesTemplate, autoStart=True)
    services.loop()

if __name__ == '__main__':
    main()
