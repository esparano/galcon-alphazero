from gzutils import logger
from domain.actions import SEND_ACTION, REDIRECT_ACTION


def commit(action):
    if action.actionType == SEND_ACTION:
        logger.send("/SEND {} {} {}\n".format(action.percent,
                                              action.sourceN, action.targetN))
    elif action.actionType == REDIRECT_ACTION:
        logger.send("/REDIR {} {}\n".format(action.sourceN, action.targetN))
