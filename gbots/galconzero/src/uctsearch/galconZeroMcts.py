import math
import numpy as np
from copy import deepcopy

from gzutils import logger
from uctsearch.mcts import Mcts
from training.trainingGame import TrainingGame
from domain.mapHelper import MapHelper
from domain.galconState import GalconState
from evaluator.randomEvaluator import RandomEvaluator
from gzutils import actionUtils


def getEnemyUserN(g):
    for item in g.items.values():
        if item.type == 'user' and not item.neutral and item.n != g.you:
            return item.n
    assert False, "Enemy user not found"


def getRefinedProbs(root):
    # TODO: replace this
    if not root.number_visits > 1:
        logger.log(
            "WARNING: cannot gen training data because no search was done. Skipping frame.")
        return None

    refinedProbs = root.child_number_visits / np.sum(root.child_number_visits)
    totalProb = np.sum(refinedProbs)
    assert math.isclose(
        totalProb, 1), "prior probabilities sum {} != 1.".format(totalProb)

    return refinedProbs


dummyEvaluator = RandomEvaluator()


class GalconZeroMcts():

    def __init__(self):
        self.firstFrame = True

    def firstFrameInit(self, g):
        self.trainingGame = TrainingGame()
        self.mapHelper = MapHelper(g.items)
        self.firstFrame = False

    def getBestMove(self, g, timeLimit=None, iterationLimit=None, evaluator=dummyEvaluator, batchSize=1, saveTrainingData=True,
                    surrenderEnabled=False, SURRENDER_THRESHOLD=-0.99, verbose=False):
        if self.firstFrame:
            self.firstFrameInit(g)

        mctsSearch = Mcts(evaluator, explorationConstant=5)

        state = GalconState(g.items, g.you, getEnemyUserN(g), self.mapHelper)
        chosenActionIndex, numVisited, rootEval = mctsSearch.search(state, batchSize, timeLimit=timeLimit,
                                                                    iterationLimit=iterationLimit, stochastic=False)
        chosenAction = state.mapActionIndexToAction(chosenActionIndex)

        self.printResults(chosenActionIndex, numVisited,
                          mctsSearch, rootEval, verbose=verbose)

        if saveTrainingData:
            refinedProbs = getRefinedProbs(mctsSearch.root)
            if refinedProbs is not None:
                # TODO: is it necessary to copy state?
                stateCopy = deepcopy(state)
                self.trainingGame.appendState(stateCopy, refinedProbs)

        if rootEval < SURRENDER_THRESHOLD and surrenderEnabled:
            actionUtils.surrender()
            actionUtils.surrender()
            logger.log("SURRENDERING, eval = {}".format(rootEval))

        return chosenAction

    def printResults(self, chosenActionIndex, numVisited, mctsSearch, rootEval, verbose=False):
        if verbose:
            logger.log("ACTION TREE:")

        currentNode = mctsSearch.root
        depth = 0
        while currentNode.children.values():
            bestChildIndex = mctsSearch.getPrincipalVariation(
                currentNode, stochastic=False)

            if verbose:
                action = mctsSearch.root.state.mapActionIndexToAction(
                    bestChildIndex)
                if depth % 2 == 0:
                    logger.log("Bot: {}".format(
                        action.detailedStr(currentNode.state.mapHelper)))
                else:
                    logger.log("Enemy: {}".format(
                        action.detailedStr(currentNode.state.mapHelper)))

            depth += 1
            currentNode = currentNode.children[bestChildIndex]

        logger.log("nodes: {}, depth: {}, eval: {:.2f}".format(
            numVisited, depth, rootEval))

    def reportGameOver(self, g, winner):
        self.trainingGame.saveGame(g.you, winner == g.you)
        self.firstFrame = True
