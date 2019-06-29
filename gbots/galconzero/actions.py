SEND_ACTION = "SEND"
REDIRECT_ACTION = "REDIR"
NULL_ACTION = "NULL"


def createSendAction(priorProb, source, target, percent):
    return (priorProb, SEND_ACTION, source, target, percent)


def createRedirectAction(priorProb, source, target):
    return (priorProb, REDIRECT_ACTION, source, target)


def createNullAction(priorProb):
    return (priorProb, NULL_ACTION)
