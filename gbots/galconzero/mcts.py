from __future__ import division

import time
import math
import random

from log import log
from actions import createNullAction

from functools import lru_cache


@lru_cache(maxsize=131072)
def optSqrt(n):
    return math.sqrt(n)


class treeNode():
    def __init__(self, state, parent=None, prevAction=None):
        self.state = state
        self.isTerminal = state.isTerminal()
        self.parent = parent
        self.prevAction = prevAction
        self.n = 0
        self.totalReward = 0
        self.q = 0
        self.children = {}
        self.actions = None
        self.isExpanded = False


class mcts():
    def __init__(self, timeLimit=None, iterationLimit=None, explorationConstant=1 / math.sqrt(2)):
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
        node = self.selectNode(self.root)
        self.backpropagate(node, node.eval)
        self.visited += 1

    # get best child of node until terminal or unexpanded node is found
    def selectNode(self, node):
        # TODO: maybe mark nodes as terminal?
        # If terminal node is selected, don't attempt to expand
        # A node with no actions is not possible because NULL_MOVE is always valid in Galcon
        while not node.isTerminal:
            if not node.isExpanded:
                self.expand(node)
                return node
            node = self.getBestChild(node)
        return node

    def expand(self, node):
        node.isExpanded = True

        assert node.actions == None, "node priors were attempted to be calculated twice"
        actions, stateEval = node.state.getPriorProbabilitiesAndEval()
        node.actions = actions
        node.eval = stateEval

    def backpropagate(self, node, reward):
        while node is not None:
            node.n += 1
            node.totalReward += reward
            node.q = node.totalReward / node.n
            node = node.parent

    def getChildNode(self, node, action):
        assert action is not None, "ERROR: action was None"
        if action not in node.children:
            newNode = treeNode(node.state.takeAction(action), node, action)
            node.children[action] = newNode
        return node.children[action]

    # This is extremely slow because it's called a lot of times... optimize this?
    # TODO: node object pooling
    # TODO: dirichlet noise if at root
    # TODO: default Q for child so you don't necessarily have to explore?
    # TODO: Skip child if at root node and child can't possibly catch up to highest_N node given remaining time/iterations
    # TODO: first play urgency
    def getBestChild(self, parent):
        bestValue = float("-inf")
        bestAction = None

        # This is extremely slow because it's called a lot of times... optimize this?

        if (parent.n < 1):
            # TODO: leela uses 1 if parent.n is 0, I think
            assert parent.n > 0, "ERROR: NODE VISITS LESS THAN 1"
        factor = self.explorationConstant * optSqrt(parent.n)

        for action in parent.actions:
            # if child exists, use parent q (minus FirstPlayUrgency constant?)
            if action in parent.children:
                childNode = parent.children[action]
                Q = childNode.q
                U = action[0] / (1 + childNode.n)
            else:
                Q = parent.q
                U = action[0]

            # log("Q: {}, U: {}, action: {}".format(Q, U, child.prevAction))
            nodeValue = Q + factor * U
            # log('nodeValue: {}, bestValue: {}'.format(nodeValue, bestValue))
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestAction = action
        return self.getChildNode(parent, bestAction)

    # returns "best" child node
    def getPrincipalVariation(self, node):
        for child in node.children.values():
            pass
            #log("child.n: {}".format(child.n))

        # If there are no actions, return null action
        if len(node.children.values()) == 0:
            return self.getChildNode(node, createNullAction(1))

        # TODO: try c.q instead of c.n
        return max(node.children.values(), key=lambda c: c.n)
