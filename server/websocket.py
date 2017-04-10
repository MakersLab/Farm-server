
import asyncio
import websockets
import logging
import time
import json

from lib.utils import loadFromFile, loadConfig, loadJsonObject

CONFIG = loadConfig('config.yml')
UPDATE_INTERVAL = CONFIG['websocket']['state-update-interval']

logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

updateTime = time.time()
connected = set()

distributedMessage = '...'
printerStateFileName = 'printer-state.json'

def shouldUpdateMessage():
    global updateTime
    if(updateTime <= time.time()):
        updateTime = time.time() + UPDATE_INTERVAL/1000
        return True
    else:
        return False

async def consumer(message):
    print('got message')

async def producer():
    print('calling')
    global distributedMessage
    if(shouldUpdateMessage()):
        distributedMessage = loadJsonObject(printerStateFileName)
        print('loaded new message')
    await asyncio.sleep(UPDATE_INTERVAL/1000)
    return json.dumps({
        'type':'printer-state',
        'data': distributedMessage['printers'],
        'timestamp': distributedMessage['timestamp'],
    })

async def consumer_handler(websocket):
    while True:
        message = await websocket.recv()
        await consumer(message)

async def producer_handler(websocket):
    while True:
        message = await producer()
        await websocket.send(message)

async def handler(websocket, path):
    global connected
    connected.add(websocket)
    consumer_task = asyncio.ensure_future(consumer_handler(websocket))
    producer_task = asyncio.ensure_future(producer_handler(websocket))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )

    for task in pending:
        task.cancel()

start_server = websockets.serve(handler, '0.0.0.0', CONFIG['websocket']['port'])

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()