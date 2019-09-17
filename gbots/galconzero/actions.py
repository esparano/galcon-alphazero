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

    def __str__(self):
        return "SEND from {} to {} at {}%".format(
            self.sourceN, self.targetN, self.percent)


class RedirectAction(Action):
    def __init__(self, sourceN, targetN):
        self.actionType = REDIRECT_ACTION
        self.sourceN = sourceN
        self.targetN = targetN

    def __str__(self):
        return "REDIRECT fleet {} to {}".format(
            self.sourceN, self.targetN)


class NullAction(Action):
    def __init__(self):
        self.actionType = NULL_ACTION

    def __str__(self):
        return "PASS"
