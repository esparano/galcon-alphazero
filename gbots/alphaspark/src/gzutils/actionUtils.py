from gzutils import logger
from domain.actionTypes import SEND_ACTION, REDIRECT_ACTION

def commitAll(actions):
    for action in actions: 
        commit(action)

def commit(action):
    if action.actionType == SEND_ACTION:
        logger.send("/SEND {} {} {}\n".format(action.percent,
                                              action.sourceN, action.targetN))
    elif action.actionType == REDIRECT_ACTION:
        logger.send("/REDIR {} {}\n".format(action.sourceN, action.targetN))

def surrender():
    logger.send("/SURRENDER")

