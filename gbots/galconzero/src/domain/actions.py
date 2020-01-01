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

    def detailedStr(self, mapHelper):
        sourceIndex = mapHelper.planetIdToSortedIdMap[self.sourceN]
        targetIndex = mapHelper.planetIdToSortedIdMap[self.targetN]
        return "SEND from x={} to x={} at {}%".format(
            sourceIndex, targetIndex, self.percent)


class RedirectAction(Action):
    def __init__(self, sourceN, targetN):
        self.actionType = REDIRECT_ACTION
        self.sourceN = sourceN
        self.targetN = targetN

    def __str__(self):
        return "REDIRECT fleet {} to {}".format(
            self.sourceN, self.targetN)

    def detailedStr(self, mapHelper):
        targetIndex = mapHelper.planetIdToSortedIdMap[self.targetN]
        return "REDIRECT fleet {} to x={}".format(
            self.sourceN, targetIndex)


class NullAction(Action):
    def __init__(self):
        self.actionType = NULL_ACTION

    def __str__(self):
        return "PASS"

    def detailedStr(self, mapHelper):
        return "PASS"

