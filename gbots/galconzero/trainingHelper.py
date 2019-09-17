import math
import numpy as np

from log import log

# TODO: refactor this so it's more reusable in bot code

# TODO: unit test all of this. Lots of potential bugs.

# TODO: move this somewhere?


def getNNInputFromState(gameState):
    # TODO: make this use NP arrays from the start
    nnInput = []
    # add planet info
    # TODO: reuse arrays instead of creating new ones??
    for _p in gameState.mapHelper.sortedPlanets:
        p = gameState.items[_p.n]
        # TODO: fleet related properties
        friendly = p.owner == gameState.playerN
        neutral = p.neutral
        enemy = friendly == neutral
        assert int(friendly) + int(neutral) + \
            int(enemy) == 1, 'planet ownership not properly identified'

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
    for f in gameState.items.values():
        if f.type == 'fleet':
            closestPlanetN = gameState.mapHelper.findClosestPlanetNToFleet(f)
            sortedPlanetId = gameState.mapHelper.planetIdToSortedIdMap[closestPlanetN]
            offset = 0 if f.owner == gameState.playerN else 3

            row = nnInput[sortedPlanetId]
            numShipsBefore = row[9 + offset]
            assert not math.isclose(f.ships, 0)
            row[9 + offset] += f.ships
            row[10 + offset] = (row[10 + offset] * numShipsBefore +
                                f.x * f.ships) / row[9 + offset]
            row[11 + offset] = (row[11 + offset] *
                                numShipsBefore + f.y * f.ships) / row[9 + offset]

    return np.array(nnInput)


class TrainingHelper():

    def __init__(self, trainingGame):
        self.trainingGame = trainingGame

    # get inputs to neural network
    # TODO: duplicate training data for all axes of symmetry and rotation
    def getTrainX(self):
        return np.array([getNNInputFromState(state) for state in self.trainingGame.states])

    # get the desired outputs of the neural network
    def getTrainY(self):
        # TODO: make sure this is a np array
        policyTrain = self.trainingGame.refinedProbs
        assert math.isclose(
            sum(policyTrain), 1), "refined probabilities sum {} != 1.".format(sum(policyTrain))

        resultBinary = 1 if self.trainingGame.result else 0
        numSamples = policyTrain.shape[0]
        valueTrain = np.full(numSamples, resultBinary)

        return [policyTrain, valueTrain]
