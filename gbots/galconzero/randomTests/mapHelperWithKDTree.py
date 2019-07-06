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


def getPlanets(items):
    return [p for p in items.values() if p.type == 'planet']


def getFleets(items):
    return [f for f in items.values() if f.type == 'fleet']


class MapHelper():

    def setItems(self, items):
        self.planets = getPlanets(items)
        self.kdTree = cKDTree([[p.x, p.y] for p in self.planets])

    # return closest num planets to x,y
    # returns 1 planet if num==1, else returns array of planets
    def queryClosestNPlanets(self, x, y, num=1):
        if num == 1:
            return self.planets[self.kdTree.query([x, y], num)[1]]
        return [self.planets[i] for i in self.kdTree.query([x, y], num)[1]]

    # returns planets within radius of x,y
    def queryPlanetsWithinRadius(self, x, y, radius):
        return [self.planets[i] for i in self.kdTree.query_ball_point([x, y], radius)]


mapHelper = MapHelper()
