import random
import numpy as np

from log import log
from gz_mathutils import dist
from nnSetup import NUM_OUTPUTS


def rateSourcePlanet(source, playerN):
    if source.owner != playerN:
        return -1000000
    return source.ships


def rateTargetPlanet(source, target, playerN):
    if target.owner == playerN:
        return -1000000
    if target.neutral:
        return -0.7*target.ships*(2) + target.production - dist(source.x, source.y, target.x, target.y)*0.18
    return -0.7*target.ships*(2 - 1.2) + target.production - dist(source.x, source.y, target.x, target.y)*0.18


def replacementPriors(items, playerN, enemyN):
    outputs = np.zeros([NUM_OUTPUTS], dtype=np.float32)
    planets = mapHelper.planets
    source = max(planets, key=lambda p: rateSourcePlanet(p, playerN))
    target = max(planets, key=lambda p: rateTargetPlanet(source, p, playerN))
    # TODO: fix this. Doesn't work at all anymore
    return [source.n, target.n]


class ClassicCopyEval:

    def getPriorProbabilitiesAndEval(self, items, playerN, enemyN):
        priors = replacementPriors(items, playerN, enemyN)
        return priors, 0
