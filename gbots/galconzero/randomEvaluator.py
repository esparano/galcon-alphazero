import numpy as np
from nnSetup import NUM_OUTPUTS
from evalUtils import applyLegalMoveMask, calculateLegalMoveMaskForState, normalizeActions


class RandomEvaluator():
    def evaluate(self, state):
        priors = np.random.random(NUM_OUTPUTS)
        applyLegalMoveMask(priors, calculateLegalMoveMaskForState(state))
        priors /= np.sum(priors)
        return priors, np.random.random()*2 - 1

    def evaluateMany(self, states):
        return [self.evaluate(state)[0] for state in states], np.random.random(len(states))*2 - 1
