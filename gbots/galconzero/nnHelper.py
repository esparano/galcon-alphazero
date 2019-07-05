import numpy as np
import random
from keras.models import load_model
from log import log
from trainingGame import TrainingGame
from trainingHelper import TrainingHelper
from actions import createNullAction, createSendAction
from nnSetup import NUM_PLANETS, NUM_ACTIONS_PER_LAYER, NUM_FEATURES, NUM_OUTPUTS

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


class NNHelper:
    def __init__(self, modelFileName):
        self.model = load_model(modelFileName)

    # TODO: THIS IS A TEMPORARY HACK TO GET AROUND LIMITATIONS
    def getNNInput(self, items, playerN):
        trainingGame = TrainingGame()
        trainingGame.appendState(items, None)
        trainingGame.userN = playerN
        helper = TrainingHelper(trainingGame)
        nnInput = helper.getNNInputFromState(items)
        nnInput = np.array([nnInput])
        return nnInput, helper

    def doPredict(self, nnOutput, helper):
        log(nnOutput)

    def predict(self, items, playerN):
        nnInput, helper = self.getNNInput(items, playerN)
        actions, stateEval = self.model.predict(nnInput)
        return self.getActionsFromNNOutput(actions[0], helper, items, playerN), stateEval[0]

    # TODO: interpret output as priors
    def getActionsFromNNOutput(self, nnOutput, trainingHelper, items, playerN):
        actions = []
        actions.append(createNullAction(nnOutput[0] + random.random()*0.1))

        for index in range(1, NUM_ACTIONS_PER_LAYER + 1):
            sourceN, targetN = trainingHelper.indexToSourceTarget(index)
            assert(sourceN != targetN)

            source = items[sourceN]
            if source.owner == playerN and source.ships > 0:
                # TODO: is this good?
                # prune bad actions but not always??
                # if nnOutput[index] > 0.0005 or random.random() > 0.8:
                    # TODO: REMOVE THE 0.02 BIAS
                actions.append(createSendAction(
                    nnOutput[index] + random.random()*0.1, sourceN, targetN, 50))

        # TODO: for now, just suppress all redirection.
        # for index in range(NUM_ACTIONS_PER_LAYER + 1, NUM_OUTPUTS):

        return actions
