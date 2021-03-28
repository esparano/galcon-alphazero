import numpy as np
from numba import njit

from domain.mapHelper import sortedSourceTargetToIndex, indexToSortedSourceTarget
from nn.nnSetup import NUM_ACTIONS_PER_LAYER, NUM_LAYERS


def getXAxisReflectedTrainingData(_trainX):
    trainX = _trainX.copy()
    for sample in trainX:
        for row in sample:
            row[8] *= -1
            row[11] *= -1
            row[14] *= -1
    return trainX

def yAxisFlipTrainX(trainX):
    flipped = np.flip(trainX, 1)
    for sample in flipped:
        for row in sample:
            row[7] *= -1
            row[10] *= -1
            row[13] *= -1
    return flipped

@njit
def getYFlippedIndex(index):
    if index == 0:
        return 0
    offset = int((index-1) / NUM_ACTIONS_PER_LAYER) * NUM_ACTIONS_PER_LAYER + 1
    return (NUM_ACTIONS_PER_LAYER - 1) - (index - 1) % NUM_ACTIONS_PER_LAYER + offset

def flipSample(sample):
    # TODO: inefficient
    newIndices = np.array([getYFlippedIndex(index)
                           for index in np.arange(sample.size)])
    return sample[newIndices]

def yAxisFlipTrainP(trainP):
    # TODO: inefficient
    return np.array([flipSample(sample) for sample in trainP])


def getYAxisReflectedTrainingData(_trainX, _trainP):
    return yAxisFlipTrainX(_trainX.copy()), yAxisFlipTrainP(_trainP.copy())
