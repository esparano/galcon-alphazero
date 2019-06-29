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
        0.15,
        random.choice(mine).n,
        random.choice(others).n,
        random.randrange(5, 100, 5)
    ) for _ in range(5)]


def testFleetActions(items, playerN, enemyN):
    mine = [f for f in getFleets(items) if f.owner == playerN]
    others = [p for p in getPlanets(items) if p.owner != playerN]
    if len(mine) == 0 or len(others) == 0:
        return []
    return [createRedirectAction(0.05,
                                 random.choice(mine).n,
                                 random.choice(others).n
                                 ) for _ in range(5)]


class EvalAndMoveGen:

    def getPriorProbabilities(self, items, playerN, enemyN):
        # TODO: undo
        # return testPlanetActions(items, playerN, enemyN) + testFleetActions(items, playerN, enemyN) + [createNullAction()]
        return [createNullAction(0.5), createNullAction(0.25), createNullAction(0.25)]

    def getEval(self, items, playerN, enemyN):
        planets = getPlanets(items)
        myPlanets = [p for p in planets if p.owner == playerN]
        enemyPlanets = [p for p in planets if p.owner !=
                        enemyN and not p.neutral]
        myProd = sum(p.production for p in myPlanets)
        enemyProd = sum(p.production for p in enemyPlanets)
        return myProd - enemyProd
