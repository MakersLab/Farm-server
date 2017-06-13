import asyncio
from aiohttp import ClientSession, FormData, MultipartWriter
import json
import uuid

COMMAND_PRINT = 'COMMAND_PRINT'
COMMAND_PAUSE = 'COMMAND_PAUSE'
COMMAND_RESUME = 'COMMAND_RESUME'
COMMAND_LOAD = 'COMMAND_LOAD'
COMMAND_CANCEL = 'COMMAND_CANCEL'
COMMAND_LOAD_FILE = 'COMMAND_LOAD_FILE'
COMMAND_PREHEAT= 'COMMAND_PREHEAT'

def addUniqueIdToFile(filename):
    splitFilename = filename.split('.')
    splitFilename[0] = '{filename}'.format(filename=splitFilename[0])
    return '.'.join(splitFilename)

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
    elif (action == COMMAND_LOAD):
        pass
    elif (action == COMMAND_CANCEL):
        body['command'] = 'cancel'
    elif (action == COMMAND_LOAD_FILE):
        body['command'] = 'select'
        body['print'] = True
    return body

async def sendCommand(session, url, apiKey, action):
    headers = {
        'X-Api-Key': apiKey
    }
    body = getRequestBody(action)
    async with session.post(url,headers=headers,json=body) as response:
        responseText = await response.text()
        return responseText, response.status


async def sendFile(session, url, apiKey, action, fileName):
    headers = {
        'X-Api-Key': apiKey
    }

    filenameWithId = addUniqueIdToFile(fileName)
    data = {}
    if(action == COMMAND_LOAD):
        data = FormData()
        data.add_field('file', open('data/file.gco','rb'), filename=filenameWithId, content_type='application/octet-stream')

    async with session.post(url,headers=headers, data=data) as response:
        await response.text()

        data = {'command': 'select'}
        async with session.post(url+'/'+filenameWithId, headers=headers, json=data) as responseCommand:
            return await responseCommand.read(), responseCommand.status

async def sendToolCommand(session, url, apiKey, toolTemperature):
    headers = {
        'X-Api-Key': apiKey
    }
    data = {
        'command': 'target',
        'targets': {
            'tool0': int(toolTemperature),
        },
    }
    async with session.post(url, headers=headers, json=data) as response:
        return await response.text(), response.status

async def sendBedCommand(session, url, apiKey, bedTemperature):
    headers = {
        'X-Api-Key': apiKey
    }
    data = {
        'command': 'target',
        'target': int(bedTemperature),
    }
    async with session.post(url, headers=headers, json=data) as response:
        return await response.text(), response.status

async def run(command, printers, fileName, toolTemperature, bedTemperature):
    print('making request')
    url = "http://googl.com/"
    tasks = []

    async with ClientSession() as session:
        apiRoute = ''
        if(command == COMMAND_LOAD):
            apiRoute = '/api/files/local'
        elif(command == COMMAND_LOAD_FILE):
            apiRoute = '/api/files/local/{0}'.format(fileName)
        elif(command == COMMAND_PREHEAT):
            apiRoute = '/api/printer/{0}'
        else:
            apiRoute = '/api/job'
        for printer in printers:
            url = 'http://{address}:{port}{apiRoute}'.format(address=printers[printer]['address'],port=printers[printer]['port'], apiRoute=apiRoute)
            if(command == COMMAND_LOAD):
                task = asyncio.ensure_future(sendFile(session, url, printers[printer]['apiKey'], command, fileName))
                tasks.append(task)
            elif( command == COMMAND_PREHEAT):

                tasks.append(asyncio.ensure_future(sendToolCommand(session, url.format('tool'), printers[printer]['apiKey'], toolTemperature)))

                tasks.append(asyncio.ensure_future(sendBedCommand(session, url.format('bed'), printers[printer]['apiKey'], bedTemperature)))
            else:
                task = asyncio.ensure_future(sendCommand(session, url, printers[printer]['apiKey'], command))
                tasks.append(task)

        responses = await asyncio.gather(*tasks)
        return responses

def makeRequest(command, printers, fileName=None, toolTemperature=None, bedTemperature=None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(run(command, printers, fileName, toolTemperature=toolTemperature, bedTemperature=bedTemperature))
    return (loop.run_until_complete(future))


