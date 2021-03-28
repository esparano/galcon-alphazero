import numpy as np

from uctsearch.mcts import childQ, childU, selectBestChild, MIN_CHILD_U, UCTNode, Mcts
from nn.nnSetup import NUM_OUTPUTS


class TestState():
    def __init__(self, move):
        self.move = move

    def takeAction(self, actionIndex):
        return TestState(actionIndex - self.move)


class TestEvaluator():
    def evaluateSingle(self, state):
        priors = np.zeros(NUM_OUTPUTS)
        for i in range(5):
            priors[i] += 0.1
        priors /= np.sum(priors)
        return priors, state.move/5 - 0.5

    def evaluateMany(self, states):
        return zip(*[self.evaluateSingle(state) for state in states])


def test_basic_search():
    evaluator = TestEvaluator()
    initialState = TestState(0)
    uctsearch = Mcts(evaluator)

    bestAction, visits = uctsearch.search(
        initialState, batchSize=10, iterationLimit=1000)
    print(visits)
