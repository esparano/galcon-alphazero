from log import send
from actions import SEND_ACTION, REDIRECT_ACTION


def commitAction(action):
    if action.actionType == SEND_ACTION:
        send("/SEND {} {} {}\n".format(action.percent,
                                       action.sourceN, action.targetN))
    elif action.actionType == REDIRECT_ACTION:
        send("/REDIR {} {}\n".format(action.sourceN, action.targetN))
