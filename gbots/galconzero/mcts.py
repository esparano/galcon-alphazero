from __future__ import division

import time
import math
import random

from numba import jit
from functools import lru_cache

from log import log


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
        self.n = 0
        self.totalReward = 0
        self.q = 0
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

        bestChild = self.getPrincipalVariation(self.root)
        return bestChild.prevAction, self.visited

    def executeRound(self):
        self.visited += 1
        node = self.selectNode(self.root)
        reward = self.rollout(node.state)
        self.backpropagate(node, reward)

    def selectNode(self, node):
        while not node.isTerminal:
            # TODO: only expand once child is selected. Don't have to expand EVERY child node because we have a default Q.
            if node.isFullyExpanded:
                node = self.getBestChild(node)
            else:
                return self.expand(node)
        return node

    def expand(self, node):
        if node.remainingActions == None:
            # Only ask the state to generate priors once, instead of len(actions) times
            node.remainingActions = node.state.getPriorProbabilities()

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
            node.n += 1
            node.totalReward += reward
            node.q = node.totalReward / node.n
            node = node.parent

    # This is extremely slow because it's called a lot of times... optimize this?
    # TODO: node object pooling
    # TODO: dirichlet noise if at root
    # TODO: default Q for child so you don't necessarily have to explore?
    # TODO: Skip child if at root node and child can't possibly catch up to highest_N node given remaining time/iterations
    # TODO: first play urgency
    def getBestChild(self, parent):
        bestValue = float("-inf")
        bestNode = None

        # This is extremely slow because it's called a lot of times... optimize this?

        if (parent.n < 1):
            # TODO: leela uses 1 if parent.n is 0, I think
            assert parent.n > 0, "ERROR: NODE VISITS LESS THAN 1"
        factor = self.explorationConstant * optSqrt(parent.n)

        for child in parent.children:
            Q = child.q if child.n > 0 else parent.q
            U = child.prevAction[0] / (1 + child.n)
            # log("Q: {}, U: {}, action: {}".format(Q, U, child.prevAction))
            nodeValue = Q + factor * U
            # log('nodeValue: {}, bestValue: {}'.format(nodeValue, bestValue))
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNode = child
        return bestNode

    def getPrincipalVariation(self, node):
        # # TODO: try c.q instead of c.n
        # for child in node.children:
        #     log("child.n: {}".format(child.n))
        return max(node.children, key=lambda c: c.n)
