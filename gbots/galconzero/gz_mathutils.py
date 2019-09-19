import math
from numba import njit

TIME_TO_DIST = 40 / 100  # normalized
PROD_TO_SHIPS_PER_SEC = 50  # normalized


@njit
def dist(x1, y1, x2, y2):
    return math.hypot(x1 - x2, y1 - y2)


@njit
def timeToDist(time):
    return time * TIME_TO_DIST


@njit
def vectorComponents(x1, y1, x2, y2, dist):
    # Return the x and y components of a vector of length "dist"
    # using the direction (x2, y2) - (x1, y1)
    angle = math.atan2(y2 - y1, x2 - x1)
    return (dist * math.cos(angle), dist * math.sin(angle))


@njit
def futureShips(neutral, ships, prod, time):
    # Return the number of ships "planet" will have "time" seconds from now
    # use numpy to process entire map at the same time
    if neutral:
        return ships

    return ships + prod / PROD_TO_SHIPS_PER_SEC * time
