import random
import math
from actions import createSendAction, createRedirectAction, createNullAction
from log import log


def getPlanets(items):
    return [p for p in items.values() if p.type == 'planet']


def getFleets(items):
    return [f for f in items.values() if f.type == 'fleet']


def testPlanetActions(items, playerN, enemyN):
    planets = getPlanets(items)
    mine = [p for p in planets if p.owner == playerN]
    others = [p for p in planets if p.owner != playerN]
    enemies = [p for p in planets if p.owner == enemyN]
    if len(mine) == 0 or len(others) == 0 or len(enemies) == 0:
        return []
    # TODO: figure out how to remove duplicates
    return [createSendAction(
        0.15,
        random.choice(mine).n,
        random.choice(others).n,
        50  # random.randrange(25, 101, 25)
    ) for _ in range(6)] + [createSendAction(
        0.4,
        random.choice(mine).n,
        random.choice(enemies).n,
        50  # random.randrange(25, 101, 25)
    ) for _ in range(9)]


def testFleetActions(items, playerN, enemyN):
    mine = [f for f in getFleets(items) if f.owner == playerN]
    others = [p for p in getPlanets(items) if p.owner != playerN]
    if len(mine) == 0 or len(others) == 0:
        return []
    return [createRedirectAction(0.05,
                                 random.choice(mine).n,
                                 random.choice(others).n
                                 ) for _ in range(1)]


def normalizeActions(actions):
    total = sum(a[0] for a in actions)
    newActions = []
    for action in actions:
        prob, *rest = action
        newActions.append(tuple([prob / total, *rest]))
    return newActions


class EvalAndMoveGen:

    def getPriorProbabilitiesAndEval(self, items, playerN, enemyN):
        # + testFleetActions(items, playerN, enemyN)
        actions = testPlanetActions(
            items, playerN, enemyN) + [createNullAction(0.05)]
        actions = normalizeActions(actions)
        return actions, self.getEval(items, playerN, enemyN)
        # return [createNullAction(0.4), createNullAction(0.25), createNullAction(0.25)] + \
        #     [createNullAction(0.01), createNullAction(0.01), createNullAction(0.01), createNullAction(0.01), createNullAction(
        #         0.01), createNullAction(0.01), createNullAction(0.01), createNullAction(0.01), createNullAction(0.01), createNullAction(0.01)]

    def getEval(self, items, playerN, enemyN):
        planets = getPlanets(items)
        myPlanets = [p for p in planets if p.owner == playerN]
        enemyPlanets = [p for p in planets if p.owner == enemyN]
        mine = sum(p.production + p.ships for p in myPlanets)
        enemy = sum(p.production + p.ships for p in enemyPlanets)
        return math.atan(mine - enemy) / (2 * math.pi)
