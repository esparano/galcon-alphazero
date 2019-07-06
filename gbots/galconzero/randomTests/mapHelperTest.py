from mapHelper import mapHelper
from trainingGame import loadTrainingGame

trainingGame = loadTrainingGame('testGame.pickle')

items1 = trainingGame.states[0]
mapHelper.setItems(items1)


def printPlanet(item):
    print('planet: {},{},{}'.format(item.n, item.x, item.y))


for item in items1.values():
    if item.type == 'planet':
        printPlanet(item)

print("____________")

closest = mapHelper.queryClosestNPlanets(0, 0)
printPlanet(closest)

closest = mapHelper.queryClosestNPlanets(0, 0, 1)
printPlanet(closest)

print("____________")

closest = mapHelper.queryClosestNPlanets(-1, 0, 4)
[printPlanet(item) for item in closest]

print("____________")
closest = mapHelper.queryClosestNPlanets(1, 1, 2)
[printPlanet(item) for item in closest]

print("____________")
closest = mapHelper.queryPlanetsWithinRadius(1, 1, 0)
print(closest)
a = [printPlanet(item) for item in closest]
