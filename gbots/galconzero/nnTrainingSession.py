import numpy as np
import random

from nnTrainingFile import getTrainingDataForNumGames

BATCH_SIZE = 128


class NNTrainingSession():

    def __init__(self, model):
        self.model = model

        self.historyPolicyValAcc = []
        self.historyValueValAcc = []

        self.historyPolicyValLoss = []
        self.historyValueValLoss = []
        self.historyValLoss = []

    def doTrain(self, num_loops, numGamesPerLoop, numEpochs=1):
        for i in range(num_loops):
            history = self.trainingLoop(numGamesPerLoop, numEpochs)

            self.historyPolicyValAcc.extend(history.history['val_policy_acc'])
            self.historyValueValAcc.extend(history.history['val_value_acc'])

            self.historyPolicyValLoss.extend(
                history.history['val_policy_loss'])
            self.historyValueValLoss.extend(history.history['val_value_loss'])
            self.historyValLoss.extend(history.history['val_loss'])

    def trainingLoop(self, numGamesPerLoop, numEpochs):
        trainX, [trainYPolicy, trainYValue], valTrainX, [valYPolicy,
                                                         valYValue] = getTrainingDataForNumGames(numGamesPerLoop)

        indices = np.arange(len(trainX))
        randomSubsetIndices = np.random.choice(
            indices, size=int(len(trainX)/10), replace=False)

        trainX = np.take(trainX, randomSubsetIndices, axis=0)
        trainYPolicy = np.take(trainYPolicy, randomSubsetIndices, axis=0)
        trainYValue = np.take(trainYValue, randomSubsetIndices, axis=0)

        return self.model.fit(trainX, [trainYPolicy, trainYValue], validation_data=(valTrainX, [valYPolicy, valYValue]), epochs=numEpochs, shuffle=True, batch_size=BATCH_SIZE)
