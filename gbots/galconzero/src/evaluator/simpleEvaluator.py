import numpy as np
from nn.nnSetup import NUM_OUTPUTS
from evaluator.evalUtils import applyLegalMoveMask, calculateLegalMoveMaskForState, normalizeActions
from domain.mapHelper import getPlanets
from gzutils import logger


def getSimpleEval(state):
    planets = getPlanets(state.items)
    myProd = sum(p.production for p in planets if p.owner ==
                 state.playerN)  # avoid divide by zero errors
    enemyProd = sum(p.production for p in planets if p.owner ==
                    state.enemyN)
    simpleEval = (myProd - enemyProd) / (myProd + enemyProd)
    return simpleEval


class SimpleEvaluator():
    def evaluate(self, state):
        # all legal moves considered equally, breaking ties randomly
        priors = np.ones(NUM_OUTPUTS) + np.random.random(NUM_OUTPUTS)*0.00001
        applyLegalMoveMask(priors, calculateLegalMoveMaskForState(state))
        priors /= np.sum(priors)
        return priors, getSimpleEval(state)

    def evaluateMany(self, states):
        results = [self.evaluate(state) for state in states]
        return [result[0] for result in results], [result[1] for result in results]
