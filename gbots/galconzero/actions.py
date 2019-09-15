SEND_ACTION = "SEND"
REDIRECT_ACTION = "REDIR"
NULL_ACTION = "NULL"


# TODO: clean up inheritance structure
class Action:
    def __init__(self):
        pass


class SendAction(Action):
    def __init__(self, sourceN, targetN, percent):
        self.actionType = SEND_ACTION
        self.sourceN = sourceN
        self.targetN = targetN
        self.percent = percent


class RedirectAction(Action):
    def __init__(self, sourceN, targetN):
        self.actionType = REDIRECT_ACTION
        self.sourceN = sourceN
        self.targetN = targetN


class NullAction(Action):
    def __init__(self):
        self.actionType = NULL_ACTION
