from copy import deepcopy

from log import log
from copy import deepcopy
import math

from mcts import mcts
from galconState import GalconState
from evalAndMoveGen import EvalAndMoveGen
from trainingGame import TrainingGame

defaultEvaluator = EvalAndMoveGen()


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


class GalconZeroMcts():
    def __init__(self):
        self.trainingGame = TrainingGame()

    def getBestMove(self, g, iterationLimit=1000, evaluator=defaultEvaluator, saveTrainingData=True):
        mctsSearch = mcts(iterationLimit=iterationLimit, explorationConstant=1)

        enemyN = getEnemyUserN(g)
        assert enemyN != g.you, "Enemy user was the same as bot user"

        state = GalconState(g.items, g.you, enemyN, evaluator)

        chosenAction, numVisited = mctsSearch.search(state)

        # for testing, print out sequences of moves
        #log("ACTION TREE:")
        currentNode = mctsSearch.root
        depth = 0
        while currentNode.children.values():
            bestChild = mctsSearch.getPrincipalVariation(currentNode)
            # log(bestChild.prevAction)

            depth += 1
            currentNode = bestChild
        #log("END ACTION TREE")

        log("nodes: {}, depth: {}, eval: {}".format(
            numVisited, depth, mctsSearch.root.q))

        if saveTrainingData:
            refinedProbs = getRefinedProbs(mctsSearch.root)
            if refinedProbs is not None:
                self.trainingGame.appendState(deepcopy(g.items), refinedProbs)

        return chosenAction

    def reportGameOver(self, g, winner):
        self.trainingGame.saveGame(g.you, winner == g.you)
        self.trainingGame = TrainingGame()
