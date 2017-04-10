import asyncio
from aiohttp import ClientSession
import json
import yaml
import time
from lib.utils import loadFromFile, loadConfig

CONFIG = loadConfig('config.yml')

JOB_INFO = 'JOB_INFO'
PRINTER_INFO = 'PRINTER_INFO'

async def fetch(url, session,apiKey,printer,dataType):
    headers = {
        'X-Api-Key': apiKey,
    }
    async with session.get(url,headers=headers) as response:
        return await response.read(),printer,dataType

async def run():
    print('Get data')
    urlJobs = "http://{address}:{port}/api/job"
    urlPrinter = "http://{address}:{port}/api/printer"
    tasks = []
    config = loadConfig('printers.yml')

    async with ClientSession() as session:
        printers = config['printers']
        for key in config['printers']:
            task = asyncio.ensure_future(fetch(
                urlJobs.format(address=printers[key]['address'],port=printers[key]['port']),
                session,printers[key]['apiKey'],key,JOB_INFO))
            tasks.append(task)
            task = asyncio.ensure_future(fetch(
                urlPrinter.format(address=printers[key]['address'],port=printers[key]['port']),
                session,printers[key]['apiKey'],key,PRINTER_INFO))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        data = {}

        for key in config['printers']:
            response_data_printer = {}
            response_data_job = {}
            for response in responses:
                if(response[1]==key):
                    if(response[2]==PRINTER_INFO):
                        response_data_printer = json.loads(response[0].decode('utf-8'))
                    elif(response[2]==JOB_INFO):
                        response_data_job = json.loads(response[0].decode('utf-8'))
            data[key] = {
                'state':response_data_printer['state']['text'],
                'progress': response_data_job['progress']['completion'],
                'nozzleTemperature': response_data_printer['temperature']['tool0']['actual'],
                'bedTemperature': response_data_printer['temperature']['bed']['actual'],
                'fileName': response_data_job['job']['file']['name'],
                'timePrinting': response_data_job['progress']['printTime'],
                'timeRemaining': response_data_job['progress']['printTimeLeft'],
            }

        data_json = json.dumps({
            'timestamp': int(time.time()),
            'printers': data,
        })
        with open('printer-state.json','w') as file:
            file.write(data_json)


loop = asyncio.get_event_loop()

nextTime = time.time()

def getData():
    future = asyncio.ensure_future(run())
    loop.run_until_complete(future)

i = 1
startTime = time.time()
expectedTime = startTime
updateInterval = int(CONFIG['printer-state']['update-interval'])
while True:
    if (nextTime > time.time()):
        time.sleep(((nextTime - time.time())))
    elif (nextTime < time.time()):
        pass
        # updateInterval += 100
        # print('Lagging behind, adding 100ms to update time interval, now is {}ms'.format(updateInterval))
    print(time.time() - (startTime+(i-1)*(updateInterval/1000)))
    getData()
    expectedTime += updateInterval
    nextTime = startTime + (i*updateInterval)/1000
    i += 1
