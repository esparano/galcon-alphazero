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

    # for testing, print out sequences of moves
    log("ACTION TREE:")
    currentNode = mctsSearch.root
    depth = 0
    while currentNode.children:
        bestChild = mctsSearch.getPrincipalVariation(currentNode)
        log(bestChild.prevAction)

        depth += 1
        currentNode = bestChild
    log("END ACTION TREE")

    log("nodes: {}, depth: {}".format(numVisited, depth))

    return chosenAction
