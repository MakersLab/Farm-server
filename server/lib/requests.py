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

def addUniqueIdToFile(filename):
    splitFilename = filename.split('.')
    splitFilename[0] = '{filename}-{id}'.format(filename=splitFilename[0], id=str(uuid.uuid4())[:6])
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
        data.add_field('file', open('upload/file.gco','rb'), filename=filenameWithId, content_type='application/octet-stream')

    async with session.post(url,headers=headers, data=data) as response:
        await response.text()

        data = {'command': 'select'}
        async with session.post(url+'/'+filenameWithId, headers=headers, json=data) as responseCommand:
            return await responseCommand.read()

async def run(command, printers, fileName):
    print('making request')
    url = "http://googl.com/"
    tasks = []

    async with ClientSession() as session:
        apiRoute = ''
        if(command == COMMAND_LOAD):
            apiRoute = '/api/files/local'
        elif(command == COMMAND_LOAD_FILE):
            apiRoute = '/api/files/local/{0}'.format(fileName)
        else:
            apiRoute = '/api/job'
        for printer in printers:
            url = 'http://{address}:{port}{apiRoute}'.format(address=printers[printer]['address'],port=printers[printer]['port'], apiRoute=apiRoute)
            if(command == COMMAND_LOAD):
                task = asyncio.ensure_future(sendFile(session, url, printers[printer]['apiKey'], command, fileName))
            else:
                task = asyncio.ensure_future(sendCommand(session, url, printers[printer]['apiKey'], command))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        return responses

def makeRequest(command, printers, fileName=None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(run(command, printers, fileName))
    return (loop.run_until_complete(future))


