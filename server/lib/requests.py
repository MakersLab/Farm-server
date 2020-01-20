import asyncio
from aiohttp import ClientSession, FormData, MultipartWriter,client_exceptions
import json
import uuid
import actions
from lib.utils import loadJsonObject, writeJsonObject
from lib.actionPermission import canPerformCommand

PRINTER_STATE_PATH = 'data/printer-state.json'
FAKE_PRINTER_STATE_PATH = 'data/fake-state.json'


def addUniqueIdToFile(filename):
    splitFilename = filename.split('.')
    splitFilename[0] = '{filename}'.format(filename=splitFilename[0])
    return '.'.join(splitFilename)

def getRequestBody(action):
    body = {}
    if (action == actions.COMMAND_PRINT):
        body['command'] = 'start'
    elif (action == actions.COMMAND_PAUSE):
        body['command'] = 'pause'
        body['action'] = 'pause'
    elif (action == actions.COMMAND_RESUME):
        body['command'] = 'pause'
        body['action'] = 'resume'
    elif (action == actions.COMMAND_LOAD):
        pass
    elif (action == actions.COMMAND_CANCEL):
        body['command'] = 'cancel'
    elif (action == actions.COMMAND_LOAD_FILE):
        body['command'] = 'select'
        body['print'] = True
    elif (action == actions.COMMAND_GET_ALL_FILES):
        body['recursive'] = False
    elif (action == actions.COMMAND_REMOVE_ALL_FILES):
        pass
    return body

async def sendCommand(session, url, apiKey, action):
    headers = {
        'X-Api-Key': apiKey
    }
    body = getRequestBody(action)
    async with session.post(url,headers=headers,json=body) as response:
        responseText = await response.text()
        return responseText, response.status


async def sendFile(session, url, apiKey, action, fileName,tempFilePath):
    headers = {
        'X-Api-Key': apiKey
    }

    filenameWithId = addUniqueIdToFile(fileName)
    data = {}
    if(action == actions.COMMAND_LOAD):
        data = FormData()
        data.add_field('file', open(tempFilePath,'rb'), filename=filenameWithId, content_type='application/octet-stream')

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

async def invalidAction():
    return 'cant perform action',400

def finishPrint(printers):
    fakePrinterState = loadJsonObject(FAKE_PRINTER_STATE_PATH)
    for printer in fakePrinterState:
        if(printer in printers):
            fakePrinterState[printer] = False
    writeJsonObject(FAKE_PRINTER_STATE_PATH,fakePrinterState)

async def deleteAllFiles(session,url,apiKey):
    headers = {
        'X-Api-Key': apiKey
    }
    body = getRequestBody(actions.COMMAND_GET_ALL_FILES)
    getUrl = url.format('')
    print("deleting")
    print('url',getUrl)

    failed = False
    async with session.get(url,headers=headers,json=body) as response:
        data = await response.text()
        data = json.loads(data)
        for file in data['files']:
            print(file['name'])
            newUrl='{0}/{1}'.format(url,file['name'])
            print(newUrl)
            print('closed',session.closed)
            response = 0
            try:
                async with session.delete(newUrl,headers=headers) as responseDelete:
                    response = responseDelete.status
            except client_exceptions.ServerDisconnectedError:
                async with session.delete(newUrl,headers=headers) as responseDelete:
                    response = responseDelete.status
            if(response != 204):
                failed = True
    if (failed):
        return 'Some deletes were unsuccesfull',409
    else:
        return 'Ok',200




async def run(command, printers, fileName, toolTemperature, bedTemperature,tempFileName=None):
    print('making request')
    tasks = []
    printerState = loadJsonObject(PRINTER_STATE_PATH)['printers']

    if(command == actions.COMMAND_FINISH):
        finishPrint(printers)
        return ['',200]

    async with ClientSession() as session:
        apiRoute = ''
        if(command == actions.COMMAND_LOAD):
            apiRoute = '/api/files/local'
        elif(command == actions.COMMAND_LOAD_FILE):
            apiRoute = '/api/files/local/{0}'.format(fileName)
        elif(command == actions.COMMAND_PREHEAT):
            apiRoute = '/api/printer/{0}'
        elif(command == actions.COMMAND_SHUTDOWN):
            apiRoute = '/api/system/commands/core/shutdown'
        elif(command == actions.COMMAND_REMOVE_ALL_FILES):
            apiRoute = '/api/files/local'
        else:
            apiRoute = '/api/job'
        for printer in printers:
            if(canPerformCommand(command, printerState[printer]['state'])):
                url = 'http://{address}:{port}{apiRoute}'.format(address=printers[printer]['address'],
                                                                 port=printers[printer]['port'], apiRoute=apiRoute)
                if (command == actions.COMMAND_LOAD):
                    task = asyncio.ensure_future(sendFile(session, url, printers[printer]['apiKey'], command, fileName,tempFileName))
                    tasks.append(task)
                elif (command == actions.COMMAND_PREHEAT):
                    tasks.append(asyncio.ensure_future(
                        sendToolCommand(session, url.format('tool'), printers[printer]['apiKey'], toolTemperature)))

                    tasks.append(asyncio.ensure_future(
                        sendBedCommand(session, url.format('bed'), printers[printer]['apiKey'], bedTemperature)))
                elif (command == actions.COMMAND_REMOVE_ALL_FILES):
                    tasks.append(asyncio.ensure_future(
                        deleteAllFiles(session,url,printers[printer]['apiKey'])
                    ))
                else:
                    task = asyncio.ensure_future(sendCommand(session, url, printers[printer]['apiKey'], command))
                    tasks.append(task)
            else:
                tasks.append(asyncio.ensure_future(invalidAction()))

        responses = await asyncio.gather(*tasks)
        print(responses)
        return responses

def makeRequest(command, printers, fileName=None, toolTemperature=None, bedTemperature=None,tempFileName=None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(run(command, printers, fileName, toolTemperature=toolTemperature, bedTemperature=bedTemperature,tempFileName=tempFileName))
    return (loop.run_until_complete(future))


