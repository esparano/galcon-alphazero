from copy import deepcopy


class GalconState():

    # actionGen and evaluator are injected
    def __init__(self, items, playerTeamN, enemyTeamN, actionGen, evaluator):
        self.items = items
        self.playerTeamN = playerTeamN
        self.enemyTeamN = enemyTeamN
        self.actionGen = actionGen
        self.evaluator = evaluator
        # TODO: expand and calculate both reward and possible actions simultaneously?
        # Then mark node as expanded and store results

    # moves are integers in 3-tuple (to, from, perc)
    # TODO: prior probabilities
    def getPossibleActions(self):
        return self.actionGen.getPossibleActions(self.items, self.playerTeamN, self.enemyTeamN)

    def takeAction(self, action):
        newItems = deepcopy(self.items)

        newState = GalconState(newItems, self.enemyTeamN,
                               self.playerTeamN, self.actionGen, self.evaluator)

        # TODO: update items after applying action
        return newState

    def isTerminal(self):
        # TODO:
        return False

    def getReward(self):
        return self.evaluator.getEval(self.items, self.playerTeamN, self.enemyTeamN)
