import math
import numpy as np

from gzutils import logger, actionUtils
from training.trainingGame import TrainingGame
from evaluator.randomEvaluator import RandomEvaluator
from domain.mapHelper import MapHelper
from domain.galconState import GalconState

def getEnemyUserN(g):
    for item in g.items.values():
        if item.type == 'user' and not item.neutral and item.n != g.you:
            return item.n
    assert False, "Enemy user not found"

dummyEvaluator = RandomEvaluator()
 
class AlphaSparkMain():

    def __init__(self):
        self.firstFrame = True

    def firstFrameInit(self, g):
        self.trainingGame = TrainingGame()
        self.mapHelper = MapHelper(g.items)
        self.firstFrame = False

    def getActions(self, g, evaluator=dummyEvaluator, saveTrainingData=False,
                    surrenderEnabled=False, SURRENDER_THRESHOLD=-0.99, verbose=False):
        if self.firstFrame:
            self.firstFrameInit(g)

        enemyN = getEnemyUserN(g)
        state = GalconState(g.items, g.you, enemyN)
        actions, evaluation = evaluator.evaluate(state)
        
        self.printResults(g, actions, evaluation, verbose=verbose)

        # save some data??
        # if saveTrainingData:
            # Is copy necessary?
            # stateCopy = deepcopy(state)
            # self.trainingGame.appendState(stateCopy, refinedProbs)

        if evaluation < SURRENDER_THRESHOLD and surrenderEnabled:
            actionUtils.surrender()
            actionUtils.surrender()
            logger.log("SURRENDERING, eval: {}".format(evaluation))

        return actions

    def printResults(self, g, actions, evaluation, verbose):
        if verbose:
            mapHelper = MapHelper(g.items)

            logger.log("ACTIONS:")
            for action in actions:
                logger.log("Bot: {}".format(
                        action.detailedStr(mapHelper)))

        logger.log("eval: {:.2f}".format(evaluation))
            
    def reportGameOver(self, g, winner):
        self.trainingGame.saveGame(g.you, winner == g.you)
        self.firstFrame = True
