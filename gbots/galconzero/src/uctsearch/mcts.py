from __future__ import division

import time
import math
import random
import collections
import numpy as np
from numba import njit, jit

from gzutils import logger

MIN_CHILD_U = -1000000


@njit
def childQ(child_total_value, child_number_visits, defaultQ):
    return np.where(child_number_visits > 0,
                    child_total_value / child_number_visits,
                    defaultQ)


@njit
def childU(child_number_visits, child_priors, number_visits):
    # return very low number to never choose illegal moves which are marked by special value '0'
    # (0 shouldn't normally be output by NN)
    # TODO: add in exploration parameter c_puct
    constFactor = np.sqrt(number_visits)  # * cpuct
    return np.where(child_priors > 0,
                    child_priors * constFactor /
                    (1 + child_number_visits),
                    MIN_CHILD_U)


@njit
def selectBestChild(explorationConst, child_total_value, child_number_visits, child_vloss, child_priors, parent_number_visits, parent_vloss, defaultQ):
    # MAKE SURE to flip child_total_value because parent is opposite player of child!
    virtual_total_value = -child_total_value - child_vloss
    virtual_number_visits = child_number_visits + child_vloss
    virtual_parent_visits = parent_number_visits + parent_vloss
    total = childQ(virtual_total_value, virtual_number_visits, defaultQ) + \
        explorationConst*childU(virtual_number_visits,
                                child_priors, virtual_parent_visits)

    bestMove = np.argmax(total)
    # logger.log("TOTAL:")
    # logger.log(childQ(virtual_total_value, virtual_number_visits, defaultQ)[bestMove])
    # logger.log(explorationConst*childU(virtual_number_visits, child_priors, virtual_parent_visits)[bestMove])
    return bestMove


class UCTNode():
    def __init__(self, state, move, parent=None):
        self.state = state
        self.move = move
        self.is_expanded = False
        self.parent = parent  # Optional[UCTNode]
        self.children = {}  # Dict[move, UCTNode]

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

    @property
    def vloss(self):
        return self.parent.child_vloss[self.move]

    @vloss.setter
    def vloss(self, value):
        self.parent.child_vloss[self.move] = value

    @property
    def avg_value(self):
        assert self.number_visits > 0, "NUMBER VISITS WAS NOT 0"
        return self.total_value / self.number_visits

    def best_child(self, explorationConst):
        return selectBestChild(explorationConst, self.child_total_value, self.child_number_visits, self.child_vloss, self.child_priors, self.number_visits, self.vloss, self.avg_value)

    def select_leaf(self, explorationConst):
        current = self
        current.vloss += 1
        while current.is_expanded:
            # Virtual losses
            # TODO: deal with case where same leaf gets chosen twice in a batch
            best_move = current.best_child(explorationConst)
            current = current.maybe_add_child(best_move)
            current.vloss += 1
        return current

    def expand(self, child_priors):
        # If a node was picked multiple times (despite vlosses), we shouldn't
        # expand it more than once.
        if self.is_expanded:
            return
        self.is_expanded = True

        self.child_priors = child_priors
        self.child_total_value = np.zeros(
            [child_priors.size], dtype=np.float32)
        self.child_number_visits = np.zeros(
            [child_priors.size], dtype=np.int32)
        self.child_vloss = np.zeros([child_priors.size], dtype=np.int32)
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
            current.total_value += perspective_value
            current.number_visits += 1
            current.vloss -= 1
            current = current.parent
            # switch perspective (eval for next player is negative of eval for current playet)
            perspective_value *= -1


class DummyNode(object):
    def __init__(self):
        self.parent = None
        self.child_total_value = collections.defaultdict(float)
        self.child_number_visits = collections.defaultdict(int)
        self.child_vloss = collections.defaultdict(int)


class Mcts():
    def __init__(self, evaluator, explorationConstant=1 / math.sqrt(2)):
        self.evaluator = evaluator
        self.explorationConstant = explorationConstant

    def setLimits(self, timeLimit, iterationLimit):
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
    def search(self, initialState, batchSize=1, stochastic=False, timeLimit=None, iterationLimit=None):
        self.setLimits(timeLimit, iterationLimit)
        self.root = UCTNode(initialState, move=None, parent=DummyNode())

        if self.limitType == 'time':
            timeLimit = time.time() + self.timeLimit / 1000
            while time.time() < timeLimit:
                self.executeBatchRound(batchSize)
                # self.executeSingleRound()
        else:
            while self.root.number_visits < self.iterationLimit:
                numToExecute = min(self.iterationLimit -
                                   self.root.number_visits, batchSize)
                self.executeBatchRound(numToExecute)
                # self.executeSingleRound()

        bestAction = self.getPrincipalVariation(self.root, stochastic)
        rootEval = self.root.total_value / self.root.number_visits
        return bestAction, self.root.number_visits, rootEval

    def executeSingleRound(self):
        # log("start: {}, {}".format(self.root.total_value, self.root.number_visits))
        leaf = self.root.select_leaf(self.explorationConstant)
        child_priors, value_estimate = self.evaluator.evaluate(leaf.state)
        leaf.expand(child_priors)
        leaf.backup(value_estimate)
        # log("end: {}, {}".format(self.root.total_value, self.root.number_visits))
        # log("value was: {}".format(value_estimate))

    def executeBatchRound(self, batchSize):
        # TODO: this approach of allowing duplicates from select_leaf may overemphasize certain results,
        # but it primarily has an effect when total allotted search time is very low because there are more duplicates at the start
        leaves = []
        while len(leaves) < batchSize:
            leaf = self.root.select_leaf(self.explorationConstant)
            leaves.append(leaf)

        child_prior_list, value_list = self.evaluator.evaluateMany(
            [leaf.state for leaf in leaves])
        for leaf, child_priors, value_estimate in zip(leaves, child_prior_list, value_list):
            leaf.expand(child_priors)
            leaf.backup(value_estimate)

    # This is extremely slow because it's called a lot of times... optimize this?
    # TODO: node object pooling
    # TODO: dirichlet noise if at root
    # TODO: default Q for child so you don't necessarily have to explore?
    # TODO: Skip child if at root node and child can't possibly catch up to highest_N node given remaining time/iterations
    # TODO: first play urgency

    # returns "best" child node
    def getPrincipalVariation(self, node, stochastic):
        selectionArray = node.child_number_visits
        # if totalVisits is 0, choose from priors instead of visits
        if node.number_visits == 1:
            logger.log(
                "WARNING: Root node not explored. Choosing from priors instead.")
            selectionArray = node.child_priors

        if stochastic:
            normalizedVisits = selectionArray / np.sum(selectionArray)
            choice = np.random.choice(
                np.arange(normalizedVisits.size), p=normalizedVisits)
            return choice
        return np.argmax(selectionArray)
