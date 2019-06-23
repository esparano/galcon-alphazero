import math
import random
from copy import deepcopy
from mcts import mcts
from eprint import eprint

def earlyEvalRolloutPolicy(state):
    return state.getReward()

def getEnemyUserN(g):
    for item in g.items.values():
        if item.type == 'user' and not item.neutral and item.n != g.you:
            return item.n
    assert False, "Enemy user not found"

def getBestMove(g, iterationLimit=1000):
    mctsSearch = mcts(iterationLimit=iterationLimit,
                      explorationConstant=1, rolloutPolicy=earlyEvalRolloutPolicy)
    
    enemyN = getEnemyUserN(g)
    assert enemyN != g.you, "Enemy user was the same as bot user"
    state = GalconState(g.items, g.you, enemyN)
    
    mctsSearch.search(state)

    # for testing, print out sequences of moves
    mctsSearch.searchLimit = 0

    chosenAction = None

    eprint("ACTION TREE:")
    currentNode = mctsSearch.root
    while currentNode.children:
        bestChild = mctsSearch.getBestChild(currentNode, 0)
        bestAction = mctsSearch.getAction(currentNode, bestChild)
        eprint(bestAction)

        if chosenAction is None:
            chosenAction = bestAction

        currentNode = bestChild

    eprint("END ACTION TREE")
    return chosenAction

class GalconState():
    # NOTE: bot is capable of fighting multiple opponents but cannot cooperate with a teammate
    def __init__(self, items, playerTeamN, enemyTeamN):
        self.items = items
        self.playerTeamN = playerTeamN
        self.enemyTeamN = enemyTeamN
        # TODO: expand and calculate both reward and possible actions simultaneously?
        # Then mark node as expanded and store results

    # moves are integers in 3-tuple (to, from, perc)
    def getRandomAction(self):
        return (1, 2, 3)

    def getPossibleActions(self):
        #myPlanets = [p for p in self.items if p.]
        # TODO:
        return [(1, 2, 3), (1, 2, 100)]

    def takeAction(self, action):
        newItems = deepcopy(self.items)

        newState = GalconState(newItems, self.enemyTeamN, self.playerTeamN)

        # TODO: update items after applying action
        return newState

    def isTerminal(self):
        # TODO: 
        return False

    def getReward(self):
        # TODO:
        return 0
