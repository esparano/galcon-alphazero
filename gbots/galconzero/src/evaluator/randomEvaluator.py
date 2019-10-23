import numpy as np

from nn.nnSetup import NUM_OUTPUTS
from evaluator.evalUtils import applyLegalMoveMask, calculateLegalMoveMaskForState, normalizeActions


class RandomEvaluator():
    def evaluate(self, state):
        priors = np.random.random(NUM_OUTPUTS)
        applyLegalMoveMask(priors, calculateLegalMoveMaskForState(state))
        priors /= np.sum(priors)
        return priors, np.random.random()*2 - 1

    def evaluateMany(self, states):
        return zip(*[self.evaluate(state)[0] for state in states])
