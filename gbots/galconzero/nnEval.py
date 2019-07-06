import random
from nnHelper import NNHelper
from actions import createSendAction, createRedirectAction, createNullAction
from log import log

from functools import lru_cache


def normalizeActions(actions):
    total = sum(a[0] for a in actions)
    newActions = []
    for action in actions:
        prob, *rest = action
        newActions.append(tuple([prob / total, *rest]))
    return newActions


class NNEval:

    def __init__(self, model='gz_dev.model'):
        self.nnHelper = NNHelper("galconzero/" + model)

    def getPriorProbabilitiesAndEval(self, items, playerN, enemyN):
        priors, predictedEval = self.nnHelper.predict(items, playerN)
        priors = normalizeActions(priors)
        return (priors, predictedEval)
