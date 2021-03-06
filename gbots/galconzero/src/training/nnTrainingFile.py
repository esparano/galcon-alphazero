import numpy as np
import random
import math

from os import listdir
from os.path import isfile, join

from nn.config import GAME_SOURCE_DIR
from training.trainingHelper import TrainingHelper
from training.trainingGame import loadTrainingGame
from training.nnTrainingDataAugmentor import getXAxisReflectedTrainingData, getYAxisReflectedTrainingData
from gzutils import logger

TRAINING_FILE_SUFFIX = ".npz"
GAME_FILE_SUFFIX = ".pickle"
VALIDATION_FILE_FRACTION = 0.1


def createTrainCacheFile(gameFile, trainingFile):
    try:
        trainingHelper = TrainingHelper(loadTrainingGame(gameFile))
    except EOFError:
        logger.log("WARNING: EOFError occurred when parsing {}".format(gameFile))
        return

    trainX = trainingHelper.getTrainX()
    trainPolicy, trainValue = trainingHelper.getTrainY()

    np.savez(trainingFile, trainX=trainX,
             trainPolicy=trainPolicy, trainValue=trainValue)


def createTrainingFileForGameIfNotExists(gameFile):
    trainingFile = gameFile.replace(GAME_FILE_SUFFIX, TRAINING_FILE_SUFFIX)
    if not isfile(trainingFile):
        createTrainCacheFile(gameFile, trainingFile)


def createTrainingFiles():
    gameFiles = [f"{GAME_SOURCE_DIR}/{fileName}" for fileName in listdir(
        GAME_SOURCE_DIR) if GAME_FILE_SUFFIX in fileName]
    for gameFile in gameFiles:
        createTrainingFileForGameIfNotExists(gameFile)


def fetchTrainXY(trainingFile):
    npzFile = np.load(trainingFile)
#     print('loaded ' + trainingCacheFile)
    return npzFile['trainX'], npzFile['trainPolicy'], npzFile['trainValue']


def getTrainingDataForFileList(filePaths):
    xValues = []
    policies = []
    evals = []

    for filePath in filePaths:
        trainX, policy, posEval = fetchTrainXY(filePath)

        # no reflection
        xValues.extend(trainX)
        policies.extend(policy)
        evals.extend(posEval)

        # reflect over x axis (reflecting over x axis does not change policy or value)
        xValues.extend(getXAxisReflectedTrainingData(trainX))
        policies.extend(policy)
        evals.extend(posEval)

        yFlippedTrainX, yFlippedPolicy = getYAxisReflectedTrainingData(
            trainX, policy)

        # reflect over y axis
        xValues.extend(yFlippedTrainX)
        policies.extend(yFlippedPolicy)
        evals.extend(posEval)

        # reflect over both y and x axis (reflecting over x axis does not change policy or value)
        xValues.extend(getXAxisReflectedTrainingData(yFlippedTrainX))
        policies.extend(yFlippedPolicy)
        evals.extend(posEval)

    return xValues, policies, evals


def getTrainingDataForNumGames(num=-1):
    allFiles = [join(GAME_SOURCE_DIR, f) for f in listdir(
        GAME_SOURCE_DIR) if TRAINING_FILE_SUFFIX in f]

    # reserve only a few games worth of files for validation only
    totalNumTrainingFiles = int(
        math.ceil(len(allFiles) * (1 - VALIDATION_FILE_FRACTION)))
    validationFiles = allFiles[totalNumTrainingFiles:]
    trainingFiles = allFiles[:totalNumTrainingFiles]

    numTrainingFiles = totalNumTrainingFiles if (num == -1) else num
    trainingFiles = trainingFiles if (
        num == -1) else random.sample(trainingFiles, numTrainingFiles)
    validationFiles = validationFiles if (num == -1) else random.sample(
        validationFiles, math.ceil(numTrainingFiles * VALIDATION_FILE_FRACTION))

    valTrainX, valYPolicy, valYValue = getTrainingDataForFileList(
        validationFiles)
    trainX, trainPolicy, trainValue = getTrainingDataForFileList(
        trainingFiles)

    # TODO: Get every 10th position. This is pretty wasteful and slow (although we don't want every position, just want to randomly sample)
    # Instead these should be NP arrays to start with, and then we should take a random percentage of that training data.
    valTrainX = np.array(valTrainX[::10])
    valYPolicy = np.array(valYPolicy[::10])
    valYValue = np.array(valYValue[::10])
    trainX = np.array(trainX)
    trainPolicy = np.array(trainPolicy)
    trainValue = np.array(trainValue)

    print("Finished loading {} training files and {} validation files".format(
        len(trainingFiles), len(validationFiles)))
    return trainX, [trainPolicy, trainValue], valTrainX, [valYPolicy, valYValue]
