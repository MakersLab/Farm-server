import actions
import states

def convertStateName(stateName):
    state = ''
    if(stateName == 'Operational'):
        state = states.STATE_READY
    elif(stateName == 'Printing'):
        state = states.STATE_PRINTING
    elif(stateName == 'Paused'):
        state = states.STATE_PAUSED
    elif(stateName == 'Finished'):
        state = states.STATE_FINISHED
    else:
        state = states.STATE_ERROR
    return state

def canPerformCommand(command, state):
    state = convertStateName(state)
    if(command == actions.COMMAND_PRINT):
        return state in [states.STATE_READY]

    elif(command == actions.COMMAND_PAUSE):
        return state in [states.STATE_PRINTING]

    elif(command == actions.COMMAND_RESUME):
        return state in [states.STATE_PAUSED]

    elif(command == actions.COMMAND_LOAD):
        return state in [states.STATE_READY]

    elif(command == actions.COMMAND_CANCEL):
        return state in [states.STATE_PRINTING,states.STATE_PAUSED]

    elif(command == actions.COMMAND_LOAD_FILE):
        return state in [states.STATE_READY]

    elif(command == actions.COMMAND_PREHEAT):
        return state in [states.STATE_READY]

    elif(command == actions.COMMAND_SHUTDOWN):
        return state in [states.STATE_FINISHED,states.STATE_READY, states.STATE_ERROR]

    elif(command == actions.COMMAND_FINISH):
        return state in [states.STATE_FINISHED]

    else:
        return False

def isFinished(previousState, newState):
    if(convertStateName(previousState['state'])in [states.STATE_PRINTING] and
               convertStateName(newState['state'])in [states.STATE_READY] and
                newState['progress'] == 100):
        return True
    else:
        return False