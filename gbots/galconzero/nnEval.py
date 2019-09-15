import random
import math
import numpy as np
from keras.models import load_model

from trainingGame import TrainingGame
from trainingHelper import TrainingHelper
from nnSetup import NUM_ACTIONS_PER_LAYER, NUM_OUTPUTS
from trainingHelper import getNNInputFromState

from log import log


# THIS IS REQUIRED TO STOP TENSORFLOW FROM USING UP ALL GPU MEMORY
# otherwise the bot can't play against itself since the first one "steals" the GPU
# note: using nvidia-smi to debug GPU usage
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
config = tf.ConfigProto(
    gpu_options=tf.GPUOptions(per_process_gpu_memory_fraction=0.3)
    # device_count = {'GPU': 1}
)
config.gpu_options.allow_growth = True
session = tf.Session(config=config)
set_session(session)


def normalizeActions(priors):
    scale = sum(priors)
    assert scale > 0, "ERROR: Priors summed to 0!!"
    # Re-normalize move_probabilities.
    priors *= 1 / scale

    priorsSum = sum(priors)
    assert math.isclose(priorsSum, 1, rel_tol=0.000001), "prior probabilities sum {} != 1.".format(
        priorsSum)

    return priors


class NNEval:

    def __init__(self, modelFileName='gz_dev.model'):
        self.model = load_model("galconzero/" + modelFileName)

    def evaluate(self, gameState):
        priors, predictedEval = self.predict(gameState)
        priors = normalizeActions(priors)
        # put eval into range [-1,1]
        return priors, 2 * predictedEval - 1

    # process single game state
    # TODO: process multiple game states
    def predict(self, gameState):
        nnInput = getNNInputFromState(gameState)
        allPriors, stateEval = self.model.predict(np.array([nnInput]))
        singlePriors = allPriors[0]
        singleEval = stateEval[0][0]
        return self.cleanNNOutput(singlePriors, gameState), singleEval

    # Adds randomness and removes illegal moves
    # TODO: separate randomness-adding and illegal-move-pruning into two different functions
    # TODO: proper randomnessInjectionIForgetTheName
    def cleanNNOutput(self, nnOutput, gameState):
        nnOutput[0] += random.random()*0.1
        for index in range(1, NUM_ACTIONS_PER_LAYER + 1):
            source, target = gameState.mapHelper.indexToSourceTarget(index)
            # assert source.n != target.n
            if source.owner == gameState.playerN and source.ships > 0:
                nnOutput[index] += random.random()*0.1
            else:
                nnOutput[index] = 0

        # TODO: UNDO THIS. for now, just suppress all redirection.
        for index in range(NUM_ACTIONS_PER_LAYER + 1, NUM_OUTPUTS):
            nnOutput[index] = 0

        return nnOutput
