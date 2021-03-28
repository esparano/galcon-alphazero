import numpy as np

from nn.nnSetup import NUM_OUTPUTS
from domain import actionTypes

class RandomEvaluator():
    def evaluate(self, state):
        actions = [actionTypes.NullAction()]
        evaluation = 0
        return actions, evaluation


    def evaluateMany(self, states):
        return zip(*[self.evaluate(state)[0] for state in states])
