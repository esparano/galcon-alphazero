import random
import math
import numpy as np
from numba import njit

from trainingGame import TrainingGame
from trainingHelper import TrainingHelper
from nnSetup import NUM_ACTIONS_PER_LAYER, NUM_OUTPUTS, NUM_PLANETS
from trainingHelper import getNNInputFromState
from nnModel import getModel

from log import log
from evalUtils import applyLegalMoveMask, calculateLegalMoveMaskForState, normalizeActions


@njit
def applyDirichletNoise(nnOutput):
    # make sure even if there are no legal moves, NULL-move is still an option.
    nnOutput[0] = nnOutput[0] if nnOutput[0] > 0.000001 else 0.000001
    pass

# TODO: inline this function?


class NNEval:

    def __init__(self, modelFileName='gz_dev.model'):
        self.model = getModel("galconzero/" + modelFileName)

    def evaluate(self, gameState):
        return self.evaluateMany([gameState])

    def evaluateMany(self, gameStates):
        priors, predictedEval = self.predict(gameStates)
        normalizeActions(priors)
        # put eval into range [-1,1]
        return priors, 2 * predictedEval[:, 0] - 1

    # process single game state
    # TODO: process multiple game states
    def predict(self, gameStates):
        allInputs = np.array([getNNInputFromState(state)
                              for state in gameStates])
        allPriors, allEvals = self.model.predict(allInputs)
        # TODO: modify priors array in place instead of doing list comprehension
        for priors, state in zip(allPriors, gameStates):
            self.cleanNNOutput(priors, state)
        return allPriors, allEvals

    def cleanNNOutput(self, nnOutput, gameState):
        applyDirichletNoise(nnOutput)
        # TODO: refactor to use a gameState.legalMoveMask
        # TODO: calculate legality only once on game state object creation (and only on planet capture), and track along with game state, then apply legal move mask to NN output
        applyLegalMoveMask(nnOutput, calculateLegalMoveMaskForState(gameState))
