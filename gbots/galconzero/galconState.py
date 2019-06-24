from copy import deepcopy


class GalconState():
    # NOTE: bot is capable of fighting multiple opponents but cannot cooperate with a teammate
    def __init__(self, items, playerTeamN, enemyTeamN):
        self.items = items
        self.playerTeamN = playerTeamN
        self.enemyTeamN = enemyTeamN
        # TODO: expand and calculate both reward and possible actions simultaneously?
        # Then mark node as expanded and store results

    # moves are integers in 3-tuple (to, from, perc)
    def getRandomAction(self):
        return (1, 2, 3)

    def getPossibleActions(self):
        # myPlanets = [p for p in self.items if p.]
        # TODO:
        return [(1, 2, 3), (1, 2, 100)]

    def takeAction(self, action):
        newItems = deepcopy(self.items)

        newState = GalconState(newItems, self.enemyTeamN, self.playerTeamN)

        # TODO: update items after applying action
        return newState

    def isTerminal(self):
        # TODO:
        return False

    def getReward(self):
        # TODO:
        return 0
