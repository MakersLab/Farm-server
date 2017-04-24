import asyncio
from aiohttp import ClientSession
import json

COMMAND_PRINT = 'COMMAND_PRINT'
COMMAND_PAUSE = 'COMMAND_PAUSE'
COMMAND_RESUME = 'COMMAND_RESUME'

def getRequestBody(action):
    body = {}
    if (action == COMMAND_PRINT):
        body['command'] = 'start'
    elif (action == COMMAND_PAUSE):
        body['command'] = 'pause'
        body['action'] = 'pause'
    elif (action == COMMAND_RESUME):
        body['command'] = 'pause'
        body['action'] = 'resume'
    return body

async def fetch(session, url, apiKey, action):
    headers = {
        'X-Api-Key': apiKey
    }
    body = getRequestBody(action)
    async with session.post(url,headers=headers,json=body) as response:
        return await response.read()

async def run(command, printers):
    print('making request')
    url = "http://googl.com/"
    tasks = []

    async with ClientSession() as session:
        for printer in printers:
            url = 'http://{address}:{port}/api/job'.format(address=printers[printer]['address'],port=printers[printer]['port'])
            task = asyncio.ensure_future(fetch(session, url, printers[printer]['apiKey'], command))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        return responses

def makeRequest(command, printers):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(run(command, printers))
    return (loop.run_until_complete(future))


