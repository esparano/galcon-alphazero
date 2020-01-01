import numpy as np
from nn.nnSetup import NUM_OUTPUTS
from evaluator.evalUtils import applyLegalMoveMask, calculateLegalMoveMaskForState, normalizeActions
from domain.mapHelper import getPlanets, getFleets
from gzutils import logger


def getSimpleEval(state):
    planets = getPlanets(state.items)
    myTotals = sum(p.production + p.ships for p in planets if p.owner ==
                   state.playerN)  # avoid divide by zero errors
    enemyTotals = sum(p.production + p.ships for p in planets if p.owner ==
                      state.enemyN)

    fleets = getFleets(state.items)
    myFleetShips = sum(f.ships for f in fleets if f.owner ==
                       state.playerN)  # avoid divide by zero errors
    enemyFleetShips = sum(f.ships for f in fleets if f.owner ==
                          state.enemyN)

    myTotals += myFleetShips
    enemyTotals += enemyFleetShips

    simpleEval = (myTotals - enemyTotals) / (myTotals + enemyTotals)
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
