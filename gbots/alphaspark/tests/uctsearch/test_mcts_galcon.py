from domain.testMapGen import genMap, FRIENDLY_USER_N, ENEMY_USER_N
from domain.mapHelper import MapHelper
from domain.galconState import GalconState
from evaluator.simpleEvaluator import SimpleEvaluator
from uctsearch.mcts import Mcts


def getTestMcts():
    evaluator = SimpleEvaluator()
    return Mcts(evaluator)


def getTestState():
    items = genMap(123)
    mapHelper = MapHelper(items)
    return GalconState(items, FRIENDLY_USER_N,
                       ENEMY_USER_N, mapHelper)


def test_simpleEvaluator():
    evaluator = SimpleEvaluator()
    startState = getTestState()
    (_, evaluation) = evaluator.evaluate(startState)
    assert evaluation == 0


def test_simpleMcts():
    mcts = getTestMcts()
    startState = getTestState()

    bestAction, numVisits = mcts.search(
        startState, batchSize=1, stochastic=False, iterationLimit=10000)
    print(bestAction)
