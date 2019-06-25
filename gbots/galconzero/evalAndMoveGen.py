import random
from actions import createSendAction, createRedirectAction, createNullAction


def getPlanets(items):
    return [p for p in items.values() if p.type == 'planet']


def getFleets(items):
    return [f for f in items.values() if f.type == 'fleet']


def testPlanetActions(items, playerN, enemyN):
    planets = getPlanets(items)
    mine = [p for p in planets if p.owner == playerN]
    others = [p for p in planets if p.owner != playerN]
    if len(mine) == 0 or len(others) == 0:
        return []
    return [createSendAction(
        random.choice(mine).n,
        random.choice(others).n,
        random.randrange(5, 100, 5)
    ) for _ in range(5)]


def testFleetActions(items, playerN, enemyN):
    mine = [f for f in getFleets(items) if f.owner == playerN]
    others = [p for p in getPlanets(items) if p.owner != playerN]
    if len(mine) == 0 or len(others) == 0:
        return []
    return [createRedirectAction(
        random.choice(mine).n,
        random.choice(others).n
    ) for _ in range(5)]


class EvalAndMoveGen:

    # TODO: prior probabilities
    def getPossibleActions(self, items, playerN, enemyN):
        # TODO: undo
        # return testPlanetActions(items, playerN, enemyN) + testFleetActions(items, playerN, enemyN) + [createNullAction()]
        return [createNullAction(), ('a'), ('b')]

    def getEval(self, items, playerN, enemyN):
        planets = getPlanets(items)
        myPlanets = [p for p in planets if p.owner == playerN]
        enemyPlanets = [p for p in planets if p.owner != enemyN]
        myProd = sum(p.production for p in myPlanets)
        enemyProd = sum(p.production for p in enemyPlanets)
        return myProd - enemyProd
