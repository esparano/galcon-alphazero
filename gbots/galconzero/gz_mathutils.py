import math

TIME_TO_DIST = 40 / 100  # normalized
PROD_TO_SHIPS_PER_SEC = 50  # normalized


def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def timeToDist(time):
    return time * TIME_TO_DIST


def prodToShipsPerSec(prod):
    return prod / PROD_TO_SHIPS_PER_SEC


def angle(source, target):
    return math.atan2(target.y - source.y, target.x - source.x)


def getVectorComponents(angle, dist):
    return (dist * math.cos(angle), dist * math.sin(angle))

# Return the number of ships "planet" will have "time" seconds from now


def futureShips(planet, time):
    if planet.neutral:
        return planet.ships

    return planet.ships + prodToShipsPerSec(planet.production) * time