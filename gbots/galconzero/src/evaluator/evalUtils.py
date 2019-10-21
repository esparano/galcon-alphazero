import numpy as np
from numba import njit

from nn.nnSetup import NUM_PLANETS, NUM_OUTPUTS


def normalizeActions(priors):
    # TODO: njit won't work. Even getting rid of linalg norm won't seem to work for me.
    # can normalize 1d or 2d arrays
    priors /= np.linalg.norm(priors, ord=1, axis=1, keepdims=True)


@njit
def setLegality(legalMoveMask, sortedPlanetIndex, legal):
    # TODO: test this
    start = 1 + (NUM_PLANETS - 1) * sortedPlanetIndex
    stop = start + (NUM_PLANETS - 1)
    legalMoveMask[start:stop] = legal


# TODO: is indexToSourceTargetN actually good? Or is it still slow? Can it be removed altogether?
def calculateLegalMoveMaskForState(gameState):
    legalMoveMask = np.zeros(NUM_OUTPUTS, dtype=bool)
    legalMoveMask[0] = True

    for i in range(NUM_PLANETS):
        source = gameState.items[gameState.mapHelper.sortedPlanets[i].n]

        # min 1 ship to send, and /100 because of NN input/output scaling
        if source.owner == gameState.playerN and source.ships >= 0.01:
            setLegality(legalMoveMask, i, True)

    return legalMoveMask


# for some reason, njit makes this slower
def applyLegalMoveMask(nnOutput, legalityMask):
    nnOutput[np.logical_not(legalityMask)] = 0
