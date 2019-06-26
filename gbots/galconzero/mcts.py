from __future__ import division

import time
import math
import random

from numba import jit
from functools import lru_cache

from log import log


@lru_cache(maxsize=131072)
def optLog(n):
    return math.log(n)


@lru_cache(maxsize=131072)
def optSqrt(n):
    return math.sqrt(n)


class treeNode():
    def __init__(self, state, parent=None, prevAction=None):
        self.state = state
        self.isTerminal = state.isTerminal()
        self.isFullyExpanded = self.isTerminal
        self.parent = parent
        self.prevAction = prevAction
        self.numVisits = 0
        self.totalReward = 0
        self.children = []
        self.remainingActions = None


class mcts():
    def __init__(self, rolloutPolicy, timeLimit=None, iterationLimit=None, explorationConstant=1 / math.sqrt(2)):
        if timeLimit != None:
            if iterationLimit != None:
                raise ValueError(
                    "Cannot have both a time limit and an iteration limit")
            # time taken for each MCTS search in milliseconds
            self.timeLimit = timeLimit
            self.limitType = 'time'
        else:
            if iterationLimit == None:
                raise ValueError(
                    "Must have either a time limit or an iteration limit")
            # number of iterations of the search
            if iterationLimit < 1:
                raise ValueError("Iteration limit must be greater than one")
            self.searchLimit = iterationLimit
            self.limitType = 'iterations'
        self.explorationConstant = explorationConstant
        self.rollout = rolloutPolicy

    def search(self, initialState):
        self.root = treeNode(initialState)

        self.visited = 0
        if self.limitType == 'time':
            timeLimit = time.time() + self.timeLimit / 1000
            while time.time() < timeLimit:
                self.executeRound()
        else:
            for _ in range(self.searchLimit):
                self.executeRound()

        bestChild = self.getBestChild(self.root, 0)
        return bestChild.prevAction, self.visited

    def executeRound(self):
        self.visited += 1
        node = self.selectNode(self.root)
        reward = self.rollout(node.state)
        self.backpropagate(node, reward)

    def selectNode(self, node):
        while not node.isTerminal:
            if node.isFullyExpanded:
                node = self.getBestChild(node, self.explorationConstant)
            else:
                return self.expand(node)
        return node

    def expand(self, node):
        if node.remainingActions == None:
            # Only ask the state to generate actions once, instead of len(actions) times
            node.remainingActions = node.state.getPossibleActions()
            random.shuffle(node.remainingActions)

        # remainingActions has already been shuffled, so this retains randomness in O(1) time
        action = node.remainingActions.pop()
        # TODO: assert action not in node.children.keys()? What about duplicate actions returned by getPossibleActions?
        if len(node.remainingActions) == 0:
            node.isFullyExpanded = True

        newNode = treeNode(node.state.takeAction(action), node, action)
        node.children.append(newNode)
        return newNode

    def backpropagate(self, node, reward):
        while node is not None:
            node.numVisits += 1
            node.totalReward += reward
            node.q = node.totalReward / node.numVisits
            node = node.parent

    def getBestChild(self, node, explorationValue):
        bestValue = float("-inf")
        bestNode = None
        # TODO: modify this to use PUCT with prior probabilities instead of UCT
        logNodeVisits = 2 * optLog(node.numVisits)
        # This is extremely slow because it's called a lot of times... optimize this?
        for child in node.children:
            nodeValue = child.q + explorationValue * \
                optSqrt(logNodeVisits / child.numVisits)
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNode = child
        return bestNode
