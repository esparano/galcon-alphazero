from mcts import mcts
from log import log
from galconState import GalconState
from evalAndMoveGen import EvalAndMoveGen

defaultActionGen = EvalAndMoveGen()
defaultEvaluator = defaultActionGen


def earlyEvalRolloutPolicy(state):
    return state.getReward()


def getEnemyUserN(g):
    for item in g.items.values():
        if item.type == 'user' and not item.neutral and item.n != g.you:
            return item.n
    assert False, "Enemy user not found"


def getBestMove(g, iterationLimit=1000, actionGen=defaultActionGen, evaluator=defaultEvaluator):
    mctsSearch = mcts(rolloutPolicy=earlyEvalRolloutPolicy,
                      timeLimit=iterationLimit, explorationConstant=1)

    enemyN = getEnemyUserN(g)
    assert enemyN != g.you, "Enemy user was the same as bot user"

    state = GalconState(g.items, g.you, enemyN, actionGen, evaluator)

    chosenAction, numVisited = mctsSearch.search(state)
    log("nodes: {}".format(numVisited))

    '''
    # for testing, print out sequences of moves
    mctsSearch.searchLimit = 0

    log("ACTION TREE:")
    currentNode = mctsSearch.root
    while currentNode.children:
        bestChild = mctsSearch.getBestChild(currentNode, 0)
        bestAction = mctsSearch.getAction(currentNode, bestChild)
        log(bestAction)

        currentNode = bestChild

    log("END ACTION TREE")
    '''

    return chosenAction
