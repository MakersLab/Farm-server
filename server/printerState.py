import asyncio
from aiohttp import ClientSession
import json
import yaml
import time
from lib.utils import loadFromFile, loadConfig, getOfflinePrinterDictionary, getUnreachablePrinterDictionary

CONFIG = loadConfig('config.yml')

JOB_INFO = 'JOB_INFO'
PRINTER_INFO = 'PRINTER_INFO'

UNREACHABLE = 'UNREACHABLE'
OFFLINE = 'OFFLINE'

async def fetch(url, session,apiKey,printer,dataType):
    headers = {
        'X-Api-Key': apiKey,
    }
    try:
        async with session.get(url,headers=headers, timeout=2) as response:
            response = await response.read()
            return response,printer,dataType
    except Exception as e:
        return UNREACHABLE,printer,dataType


async def run():
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
                    try:
                        if(response[2]==PRINTER_INFO and response[0] != UNREACHABLE):
                                response_data_printer = json.loads(response[0].decode('utf-8'))
                        elif(response[2]==JOB_INFO and response[0] != UNREACHABLE):
                            response_data_job = json.loads(response[0].decode('utf-8'))
                        else:
                            response_data_printer = UNREACHABLE
                            response_data_job = UNREACHABLE
                    except Exception as e:
                        response_data_printer = OFFLINE
                        response_data_job = OFFLINE
            if(response_data_printer != OFFLINE and response_data_printer != UNREACHABLE):
                data[key] = {
                    'state':response_data_printer['state']['text'],
                    'progress': response_data_job['progress']['completion'],
                    'nozzleTemperature': response_data_printer['temperature']['tool0']['actual'],
                    'bedTemperature': response_data_printer['temperature']['bed']['actual'],
                    'fileName': response_data_job['job']['file']['name'],
                    'timePrinting': response_data_job['progress']['printTime'],
                    'timeRemaining': response_data_job['progress']['printTimeLeft'],
                }
            elif(response_data_printer == OFFLINE):
                data[key] = getOfflinePrinterDictionary()
            elif(response_data_printer == UNREACHABLE):
                data[key] = getUnreachablePrinterDictionary()

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
    try:
        if (nextTime > time.time()):
            timeToSleep = nextTime - time.time()
            if(timeToSleep > 15):
                print('Time to sleep is too big next time {0} time{1} '.format(nextTime,time.time()))
                timeToSleep = 15
            time.sleep(((nextTime - time.time())))
        elif (nextTime < time.time()):
            pass
            # updateInterval += 100
            # print('Lagging behind, adding 100ms to update time interval, now is {}ms'.format(updateInterval))
        print('{}: Time difference from expected'.format(time.time()),time.time() - (startTime+(i-1)*(updateInterval/1000)))
        getData()
        expectedTime += updateInterval
        nextTime = startTime + (i*updateInterval)/1000
        i += 1
    except Exception as e:
        print(e)
        time.sleep(2)
