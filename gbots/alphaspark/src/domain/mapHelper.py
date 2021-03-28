# represent a single map, which provides optimized queries about planets which don't change positions

# o = Item(
# n
# type
# x
# y
# production
# radius
# )
# The only unique thing about planets is their number of ships, owner, and neutral, so the other info can be saved and copied.
#

from scipy.spatial import cKDTree
from functools import lru_cache
from numba import njit

from domain.actionTypes import SendAction, RedirectAction, NullAction
from nn.nnSetup import NUM_PLANETS, NUM_ACTIONS_PER_LAYER


def getPlanets(items):
    return [p for p in items.values() if p.type == 'planet']


def getFleets(items):
    return [f for f in items.values() if f.type == 'fleet']

# Provides optimized queries about the game state. Only needs to be computed once, at the

# sort by, for example, x value or prod? so that similar planets are always put into each node slot


def getSortedPlanets(items):
    allPlanets = [p for p in items.values() if p.type == 'planet']
    allPlanets.sort(key=lambda p: p.x)
    return allPlanets


@njit
def indexToSortedSourceTarget(index):
    source = int((index - 1) / (NUM_PLANETS - 1))
    target = (index - 1) % (NUM_PLANETS - 1)
    if target >= source:
        target += 1
    return source, target


@njit
def sortedSourceTargetToIndex(source, target):
    return 1 + source * (NUM_PLANETS - 1) + (target if target < source else target - 1)


class MapHelper():

    def __init__(self, items):
        self.sortedPlanets = getSortedPlanets(items)

        self.kdTree = cKDTree([[p.x, p.y] for p in self.sortedPlanets])

        self.planetIdToSortedIdMap = {
            p.n: i for i, p in enumerate(self.sortedPlanets)}

        # TODO: is this necessary now that MapHelper is instantiated once per game?
        self.queryClosestNPlanets.cache_clear()
        self.queryPlanetsWithinRadius.cache_clear()
        self.indexToSourceTargetN.cache_clear()

    # return closest num planets to x,y
    # returns 1 planet if num==1, else returns array of planets
    # TODO: it turns out that KD trees are not any faster than brute force for 22 planets.

    @lru_cache(maxsize=2048)
    def queryClosestNPlanets(self, x, y, num=1):
        if num == 1:
            return self.sortedPlanets[self.kdTree.query([x, y], num)[1]]
        return [self.sortedPlanets[i] for i in self.kdTree.query([x, y], num)[1]]

    # returns planets within radius of x,y
    @lru_cache(maxsize=2048)
    def queryPlanetsWithinRadius(self, x, y, radius):
        return [self.sortedPlanets[i] for i in self.kdTree.query_ball_point([x, y], radius)]

    def sendMoveToIndex(self, action: SendAction):
        source = self.planetIdToSortedIdMap[action.sourceN]
        target = self.planetIdToSortedIdMap[action.targetN]
        return sortedSourceTargetToIndex(source, target)

    def redirectMoveToIndex(self, action: RedirectAction, currentItems):
        fleet = currentItems[action.sourceN]
        targetN = action.targetN
        proxyPlanetId = self.findClosestPlanetNToFleet(fleet)
        #print("proxy planet: {} {}, fleet: {} {}".format(items[proxyPlanetId].x, items[proxyPlanetId].y, items[fleetId].x, items[fleetId].y))
        # TODO: this will have to be updated after adding percentages
        return sortedSourceTargetToIndex(proxyPlanetId, targetN) + NUM_ACTIONS_PER_LAYER

    def findClosestPlanetNToFleet(self, fleet):
        # use gridding and caching to quickly get approximately closest planet
        return self.queryClosestNPlanets(
            round(fleet.x * 5) / 5, round(fleet.y * 5) / 5).n

    def nullMoveToIndex(self, action: NullAction):
        return 0

    @lru_cache(maxsize=1024)
    def indexToSourceTargetN(self, index):
        # TODO: increase LRU cache size when redirection is added
        sourceIndex, targetIndex = indexToSortedSourceTarget(index)
        return self.sortedPlanets[sourceIndex].n, self.sortedPlanets[targetIndex].n
