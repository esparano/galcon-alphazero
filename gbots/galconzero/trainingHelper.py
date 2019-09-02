import math
import numpy as np

from actions import SEND_ACTION, REDIRECT_ACTION
from nnSetup import NUM_PLANETS, NUM_FEATURES, NUM_OUTPUTS
from mapHelper import mapHelper
from log import log

# TODO: refactor this so it's more reusable in bot code

from functools import lru_cache


@lru_cache(maxsize=8192)
def indexToSourceTargetN(index):
    source = int((index - 1) / (NUM_PLANETS - 1))
    target = (index - 1) % (NUM_PLANETS - 1)
    if target >= source:
        target += 1
    return source, target


class TrainingHelper():

    def __init__(self, trainingGame):
        self.trainingGame = trainingGame

        sortedPlanets = self.getPlanetsSorted(self.trainingGame.states[0])
        self.planetIdToSortedIdMap = {
            p.n: i for i, p in enumerate(sortedPlanets)}
        self.sortedPlanets = [p for p in sortedPlanets]

    # sort by, for example, x value or prod? so that similar planets are always put into each node slot
    def getPlanetsSorted(self, items):
        allPlanets = [p for p in items.values() if p.type == 'planet']
        allPlanets.sort(key=lambda p: p.x)
        return allPlanets

    def sendMoveToIndex(self, action):
        (_, _, source, target, _) = action
        return self.sourceTargetToIndex(source, target)

    def redirectMoveToIndex(self, action, items):
        (_, _, fleetId, target) = action
        proxyPlanetId = self.findClosestPlanetNToFleet(items[fleetId])
        #print("proxy planet: {} {}, fleet: {} {}".format(items[proxyPlanetId].x, items[proxyPlanetId].y, items[fleetId].x, items[fleetId].y))
        # TODO: this will have to be updated when I add percentages
        return self.sourceTargetToIndex(proxyPlanetId, target) + NUM_PLANETS * (NUM_PLANETS - 1)

    def nullMoveToIndex(self, action):
        return 0

    def sourceTargetToIndex(self, sourceN, targetN):
        source = self.planetIdToSortedIdMap[sourceN]
        target = self.planetIdToSortedIdMap[targetN]
        return 1 + source * (NUM_PLANETS - 1) + (target if target < source else target - 1)

    def indexToSourceTarget(self, index):
        sourceIndex, targetIndex = indexToSourceTargetN(index)
        return self.sortedPlanets[sourceIndex], self.sortedPlanets[targetIndex]

    # TODO: use KD trees to speed up nearest neighbor searches.
    def getSortedPlanetIdDistToFleet(self, n, f):
        items = self.trainingGame.states[0]
        p = items[n]
        return math.sqrt((p.x - f.x)**2 + (p.y - f.y)**2)

    def findClosestPlanetNToFleet(self, fleet):
        # use gridding and caching to quickly get approximately closest planet
        return mapHelper.queryClosestNPlanets(
            round(fleet.x * 5) / 5, round(fleet.y * 5) / 5).n

    # TODO: unit test all of this. Lots of potential bugs.
    def getNNInputFromState(self, items):
        nnInput = []
        # add planet info
        # TODO: reuse arrays instead of creating new ones??
        for _p in self.sortedPlanets:
            p = items[_p.n]
            # TODO: fleet related properties
            friendly = p.owner == self.trainingGame.userN
            neutral = p.neutral
            enemy = friendly == neutral
            assert int(friendly) + int(neutral) + \
                int(enemy) == 1, 'planet ownership not properly identified'

            # log("p.owner: {}, user: {}, friendly: {}, neutral:{}, enemy: {}".format(
            #     p.owner, self.trainingGame.userN, friendly, neutral, enemy))

            friendlyProd = p.production if friendly else 0
            enemyProd = p.production if enemy else 0
            neutralProd = p.production if neutral else 0
            friendlyShips = p.ships if friendly else 0
            enemyShips = p.ships if enemy else 0
            neutralShips = p.ships if neutral else 0

            # TODO: normalize data
            thisNodeData = [friendlyProd, enemyProd, neutralProd, friendlyShips,
                            enemyShips, neutralShips, p.radius, p.x, p.y, 0, 0, 0, 0, 0, 0]
            nnInput.append(thisNodeData)

        # add fleet info
        for f in items.values():
            if f.type == 'fleet':
                closestPlanetN = self.findClosestPlanetNToFleet(f)
                sortedPlanetId = self.planetIdToSortedIdMap[closestPlanetN]
                offset = 0 if f.owner == self.trainingGame.userN else 3

                row = nnInput[sortedPlanetId]
                numShipsBefore = row[9 + offset]
                assert not math.isclose(f.ships, 0)
                row[9 + offset] += f.ships
                row[10 + offset] = (row[10 + offset] * numShipsBefore +
                                    f.x * f.ships) / row[9 + offset]
                row[11 + offset] = (row[11 + offset] *
                                    numShipsBefore + f.y * f.ships) / row[9 + offset]

        return nnInput

    def getDesiredNNOutputFromRefinedProbs(self, probs, items):
        nnOutput = [0 for _ in range(NUM_OUTPUTS)]
        for (action, refinedProb) in probs:
            if action[1] == SEND_ACTION:
                index = self.sendMoveToIndex(action)
            elif action[1] == REDIRECT_ACTION:
                index = self.redirectMoveToIndex(action, items)
                #print("action {} mapped to index {}".format(action, index))
            else:
                index = self.nullMoveToIndex(action)

            # TODO: this should only be assigned once once percentages are included in network
            # assert nnOutput[index] == 0

            nnOutput[index] += refinedProb

        assert math.isclose(
            sum(nnOutput), 1), "refined probabilities sum {} != 1.".format(sum(nnOutput))
        return nnOutput

    # get inputs to neural network
    # TODO: duplicate training data for all axes of symmetry and rotation
    def getTrainX(self):
        return np.array([self.getNNInputFromState(items) for items in self.trainingGame.states])

    # get the desired outputs of the neural network
    def getTrainY(self):
        policyTrain = np.array([self.getDesiredNNOutputFromRefinedProbs(
            probs, items) for probs, items in zip(self.trainingGame.refinedProbs, self.trainingGame.states)])
        resultBinary = 1 if self.trainingGame.result else 0

        numSamples = policyTrain.shape[0]

        valueTrain = np.full(numSamples, resultBinary)
        return [policyTrain, valueTrain]
