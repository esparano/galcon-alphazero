from copy import deepcopy
import numpy as np

from log import log
from copy import deepcopy
import math

from mcts2 import mcts
from trainingGame import TrainingGame
from mapHelper import MapHelper
from galconState import GalconState
from nnSetup import NUM_OUTPUTS


def getEnemyUserN(g):
    for item in g.items.values():
        if item.type == 'user' and not item.neutral and item.n != g.you:
            return item.n
    assert False, "Enemy user not found"


def getRefinedProbs(root):
    if not root.n > 1:
        log("WARNING: cannot gen training data because no search was done. Skipping frame.")
        return None

    refinedProbs = [(child.prevAction, child.n / (root.n - 1))
                    for child in root.children.values()]
    totalProb = sum([p[1] for p in refinedProbs])
    assert math.isclose(
        totalProb, 1), "prior probabilities sum {} != 1.".format(totalProb)

    return refinedProbs


class DummyEvaluator():
    def evaluate(self, state):
        return np.random.random([NUM_OUTPUTS]), np.random.random()


dummyEvaluator = DummyEvaluator()


class GalconZeroMcts():

    def __init__(self):
        self.firstFrame = True

    def firstFrameInit(self, g):
        self.trainingGame = TrainingGame()
        self.mapHelper = MapHelper(g.items)
        self.firstFrame = False

    def getBestMove(self, g, timeLimit=None, iterationLimit=None, evaluator=dummyEvaluator, saveTrainingData=True):
        if self.firstFrame:
            self.firstFrameInit(g)

        mctsSearch = mcts(evaluator, timeLimit=timeLimit,
                          iterationLimit=iterationLimit, explorationConstant=1)

        enemyN = getEnemyUserN(g)
        assert enemyN != g.you, "Enemy user was the same as bot user"

        state = GalconState(g.items, g.you, enemyN, self.mapHelper)
        chosenActionIndex, numVisited = mctsSearch.search(state)
        chosenAction = state.mapActionIndexToAction(chosenActionIndex)

        self.printResults(chosenActionIndex, numVisited, mctsSearch, False)

        if False:  # saveTrainingData:
            refinedProbs = getRefinedProbs(mctsSearch.root)
            if refinedProbs is not None:
                # TODO: is it necessary to copy state?
                self.trainingGame.appendState(deepcopy(state), refinedProbs)

        return chosenAction

    def printResults(self, chosenActionIndex, numVisited, mctsSearch, verbose=False):
        if verbose:
            log("ACTION TREE:")

        currentNode = mctsSearch.root
        depth = 0
        while currentNode.children.values():
            bestChildIndex = mctsSearch.getPrincipalVariation(
                currentNode, stochastic=False)

            if verbose:
                action = mctsSearch.root.state.mapActionIndexToAction(
                    bestChildIndex)
                if depth % 2 == 0:
                    log("Bot: {}".format(str(action)))
                else:
                    log("Enemy: {}".format(str(action)))

            depth += 1
            currentNode = currentNode.children[bestChildIndex]

        log("nodes: {}, depth: {}, eval: {:.2f}".format(
            numVisited, depth, mctsSearch.root.total_value / mctsSearch.root.number_visits))

    def reportGameOver(self, g, winner):
        self.trainingGame.saveGame(g.you, winner == g.you)
        self.firstFrame = True
