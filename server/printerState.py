import asyncio
from aiohttp import ClientSession
import json
import yaml
import time
from lib.utils import loadFromFile, loadConfig

CONFIG = loadConfig('config.yml')

async def fetch(url, session,apiKey,printer):
    headers = {
        'X-Api-Key': apiKey,
    }
    async with session.get(url,headers=headers) as response:
        return await response.read(),printer

async def run():
    print('Get data')
    url = "http://{address}:{port}/api/job"
    tasks = []
    config = loadConfig('printers.yml')

    async with ClientSession() as session:
        printers = config['printers']
        for key in config['printers']:
            task = asyncio.ensure_future(fetch(
                url.format(address=printers[key]['address'],port=printers[key]['port']),
                session,printers[key]['apiKey'],key))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        data = {}
        for response in responses:
            data[response[1]] = json.loads(response[0].decode('utf-8'))
        data_json = json.dumps(data)
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
        updateInterval += 100
        print('Lagging behind, adding 100ms to update time interval, now is {}ms'.format(updateInterval))
    print(time.time() - (startTime+(i-1)*(updateInterval/1000)))
    getData()
    expectedTime += updateInterval
    nextTime = startTime + (i*updateInterval)/1000
    i += 1
