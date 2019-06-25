SEND_ACTION = "s"
REDIRECT_ACTION = "r"
NULL_ACTION = "n"


def createSendAction(source, target, percent):
    return (SEND_ACTION, source, target, percent)


def createRedirectAction(source, target):
    return (REDIRECT_ACTION, source, target)


def createNullAction():
    return (NULL_ACTION)
