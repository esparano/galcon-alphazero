import random
import math
import numpy as np

from trainingGame import TrainingGame
from trainingHelper import TrainingHelper
from nnSetup import NUM_ACTIONS_PER_LAYER, NUM_OUTPUTS
from trainingHelper import getNNInputFromState
from nnModel import getModel

from log import log

# can normalize 1d or 2d arrays
def normalizeActions(priors):
    priors /= np.linalg.norm(priors, ord=1, axis=1, keepdims=True)

    # for i in range(0, len(priors)):
    #     priorsSum = sum(priors[i])
    #     assert math.isclose(priorsSum, 1, rel_tol=0.000001), "prior probabilities sum {} != 1.".format(
    #         priorsSum)

    return priors


class NNEval:

    def __init__(self, modelFileName='gz_dev.model'):
        self.model = getModel("galconzero/" + modelFileName)

    def evaluate(self, gameState):
        return self.evaluateMany([gameState])

    def evaluateMany(self, gameStates):
        priors, predictedEval = self.predict(gameStates)
        priors = normalizeActions(priors)
        # put eval into range [-1,1]
        return priors, 2 * predictedEval - 1

    # process single game state
    # TODO: process multiple game states
    def predict(self, gameStates):
        allInputs = np.array([getNNInputFromState(state)
                              for state in gameStates])
        allPriors, allEvals = self.model.predict(allInputs)
        # TODO: modify priors array in place instead of doing list comprehension
        cleanedPriors = np.array([self.cleanNNOutput(priors, state)
                                  for priors, state in zip(allPriors, gameStates)])
        return cleanedPriors, allEvals

    # Adds randomness and removes illegal moves
    # TODO: separate randomness-adding and illegal-move-pruning into two different functions
    # TODO: compute illegal move mask and copy it as part of Map state, any time planet is captured, update legal moves accordingly.
    # TODO: proper Dirichlet noise
    def cleanNNOutput(self, nnOutput, gameState):
        # make sure even if there are no legal moves, NULL-move is still an option.
        nnOutput[0] = nnOutput[0] if nnOutput[0] > 0.000001 else 0.000001
        # nnOutput[0] += random.random()*0.1
        for index in range(1, NUM_ACTIONS_PER_LAYER + 1):
            firstFrameSourceN, firstFrameTargetN = gameState.mapHelper.indexToSourceTargetN(
                index)

            source = gameState.items[firstFrameSourceN]
            target = gameState.items[firstFrameTargetN]
            assert source.n != target.n

            # min 1 ship to send, and /100 because of NN input/output scaling
            if source.owner == gameState.playerN and source.ships >= 0.01:
                # TODO: this is not proper dirichlet noise
                nnOutput[index] += random.random()*0.0005
                pass
            else:
                nnOutput[index] = 0

        # TODO: UNDO THIS. for now, just suppress all redirection.
        nnOutput[NUM_ACTIONS_PER_LAYER + 1:] = 0

        return nnOutput
