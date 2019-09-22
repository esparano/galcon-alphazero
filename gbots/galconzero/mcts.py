from __future__ import division

import time
import math
import random
import collections
import numpy as np

from log import log
from nnSetup import NUM_OUTPUTS

from functools import lru_cache


class UCTNode():
    def __init__(self, state, move, parent=None):
        self.state = state
        self.move = move
        self.is_expanded = False
        self.parent = parent  # Optional[UCTNode]
        self.children = {}  # Dict[move, UCTNode]
        self.child_priors = np.zeros([NUM_OUTPUTS], dtype=np.float32)
        self.child_total_value = np.zeros(
            [NUM_OUTPUTS], dtype=np.float32)
        self.child_number_visits = np.zeros(
            [NUM_OUTPUTS], dtype=np.int32)

    @property
    def number_visits(self):
        return self.parent.child_number_visits[self.move]

    @number_visits.setter
    def number_visits(self, value):
        self.parent.child_number_visits[self.move] = value

    @property
    def total_value(self):
        return self.parent.child_total_value[self.move]

    @total_value.setter
    def total_value(self, value):
        self.parent.child_total_value[self.move] = value

    def child_Q(self):
        return self.child_total_value / (1 + self.child_number_visits)

    def child_U(self):
        # return very low number to never choose illegal moves which are marked by special value '0'
        # (0 shouldn't normally be output by NN)
        return np.where(self.child_priors > 0,
                        np.sqrt(self.number_visits) * (
                            self.child_priors / (1 + self.child_number_visits)),
                        -1000000)

    def best_child(self):
        return np.argmax(self.child_Q() + self.child_U())

    def select_leaf(self):
        current = self
        current.number_visits += 1
        current.total_value -= 1
        while current.is_expanded:
            # Virtual losses
            # TODO: deal with case where same leaf gets chosen twice in a batch
            best_move = current.best_child()
            current = current.maybe_add_child(best_move)
            current.number_visits += 1
            current.total_value -= 1
        return current

    def expand(self, child_priors):
        # If a node was picked multiple times (despite vlosses), we shouldn't
        # expand it more than once.
        if self.is_expanded:
            return
        self.is_expanded = True

        self.child_priors = child_priors
        # TODO: Q seeding (see incorporate_results in mcts.py, or Leela for examples)

    def maybe_add_child(self, move):
        if move not in self.children:
            self.children[move] = UCTNode(
                self.state.takeAction(move), move, parent=self)
        return self.children[move]

    def backup(self, value_estimate: float):
        current = self
        perspective_value = value_estimate
        while current.parent is not None:
            current.total_value += perspective_value + 1
            current = current.parent
            # switch perspective (eval for next player is negative of eval for current playet)
            perspective_value *= -1


class DummyNode(object):
    def __init__(self):
        self.parent = None
        self.child_total_value = collections.defaultdict(float)
        self.child_number_visits = collections.defaultdict(int)


class mcts():
    def __init__(self, evaluator, timeLimit=None, iterationLimit=None, explorationConstant=1 / math.sqrt(2)):
        self.evaluator = evaluator
        self.explorationConstant = explorationConstant

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
            self.iterationLimit = iterationLimit
            self.limitType = 'iterations'

    # disable stochastic for competitive play
    def search(self, initialState, batchSize, stochastic=True):
        self.root = UCTNode(initialState, move=None, parent=DummyNode())

        if self.limitType == 'time':
            timeLimit = time.time() + self.timeLimit / 1000
            while time.time() < timeLimit:
                self.executeBatchRound(batchSize)
                # self.executeSingleRound()
        else:
            while self.root.number_visits < self.iterationLimit:
                self.executeBatchRound(batchSize)
                # self.executeSingleRound()

        bestAction = self.getPrincipalVariation(self.root, stochastic)
        return bestAction, self.root.number_visits

    def executeSingleRound(self):
        # log("start: {}, {}".format(self.root.total_value, self.root.number_visits))
        leaf = self.root.select_leaf()
        child_priors, value_estimate = self.evaluator.evaluate(leaf.state)
        leaf.expand(child_priors)
        leaf.backup(value_estimate)
        # log("end: {}, {}".format(self.root.total_value, self.root.number_visits))
        # log("value was: {}".format(value_estimate[0]))

    def executeBatchRound(self, batchSize):
        # TODO: this approach of allowing duplicates from select_leaf may overemphasize certain results,
        # but it primarily has an effect when total allotted search time is very low because there are more duplicates at the start
        leaves = []
        while len(leaves) < batchSize:
            leaf = self.root.select_leaf()
            leaves.append(leaf)

        child_prior_list, value_list = self.evaluator.evaluateMany(
            [leaf.state for leaf in leaves])
        for leaf, child_priors, value_estimate in zip(leaves, child_prior_list, value_list):
            leaf.expand(child_priors)
            leaf.backup(value_estimate[0])

    # This is extremely slow because it's called a lot of times... optimize this?
    # TODO: node object pooling
    # TODO: dirichlet noise if at root
    # TODO: default Q for child so you don't necessarily have to explore?
    # TODO: Skip child if at root node and child can't possibly catch up to highest_N node given remaining time/iterations
    # TODO: first play urgency

    # returns "best" child node
    def getPrincipalVariation(self, node, stochastic):
        if stochastic:
            normalizedVisits = (node.child_number_visits /
                                np.sum(node.child_number_visits))
            choice = np.random.choice(
                np.arange(normalizedVisits.size), p=normalizedVisits)
            return choice
        return np.argmax(node.child_number_visits)
