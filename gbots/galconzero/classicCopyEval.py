import random
from log import log
from actions import createSendAction, createRedirectAction, createNullAction
from gz_mathutils import dist
from mapHelper import mapHelper


def rateSourcePlanet(source, playerN):
    if source.owner != playerN:
        return -1000000
    return source.ships


def rateTargetPlanet(source, target, playerN):
    if target.owner == playerN:
        return -1000000
    if target.neutral:
        return -0.7*target.ships*(2) + target.production - dist(source, target)*0.18
    return -0.7*target.ships*(2 - 1.2) + target.production - dist(source, target)*0.18


def replacementPriors(items, playerN, enemyN):
    planets = mapHelper.planets
    source = max(planets, key=lambda p: rateSourcePlanet(p, playerN))
    target = max(planets, key=lambda p: rateTargetPlanet(source, p, playerN))
    return [createSendAction(1, source.n, target.n, 50)]


class ClassicCopyEval:

    def getPriorProbabilitiesAndEval(self, items, playerN, enemyN):
        priors = replacementPriors(items, playerN, enemyN)
        return priors, 0
