import random

from domain.models import Item

NEUTRAL_USER_N = 1
FRIENDLY_USER_N = 2
ENEMY_USER_N = 3
FRIENDLY_HOME_N = 4
ENEMY_HOME_N = 5
NEUTRAL_START_N = 6

NUM_NEUTRALS_PER_SIDE = 10


def genMap(seed):
    random.seed(seed)
    items = []
    items.extend(genUsers())
    items.extend(genPlanets())

    dictItems = {}
    for item in items:
        dictItems[item.n] = item
    return dictItems


def genUser(n, name, c, team):
    return Item(
        n=n,
        type="user",
        name=name,
        color=c,
        team=team,
        xid=1234,
        neutral=(n == NEUTRAL_USER_N),  # questionable. Might change.
    )


def genPlanet(n, o, s, x, y, p, r):
    return Item(
        n=n,
        type="planet",
        owner=o,
        ships=s/100,
        x=x/100,
        y=y/100,
        production=p/100,
        radius=r/100,
        neutral=(o == 1),  # questionable. Might change.
    )


def genFleet(n, o, s, x, y, source, target, r):
    return Item(
        n=n,
        type="fleet",
        owner=o,
        ships=s/100,
        x=x/100,
        y=y/100,
        source=source,
        target=target,
        radius=r/100,
        xid=1234,
    )


def genUsers():
    users = []
    users.append(genUser(NEUTRAL_USER_N, "neutral", 10, NEUTRAL_USER_N))
    users.append(genUser(FRIENDLY_USER_N, "player1", 20, FRIENDLY_USER_N))
    users.append(genUser(ENEMY_USER_N, "player2", 30, ENEMY_USER_N))
    return users


def genPlanets():
    planets = []
    planets.extend(genHomes())
    planets.extend(genNeutrals())
    return planets


def genNeutrals():
    planets = []
    n = NEUTRAL_START_N
    for _ in range(NUM_NEUTRALS_PER_SIDE):
        x = (random.random() * 2 - 1) * 200
        y = (random.random() * 2 - 1) * 120
        s = random.random() * 50
        p = random.random() * 85 + 15
        r = (p*12/5 + 168)/17
        planets.append(genPlanet(n, NEUTRAL_USER_N, s, x, y, p, r))
        n += 1
        planets.append(genPlanet(n, NEUTRAL_USER_N, s, -x, -y, p, r))
        n += 1
    return planets


def genHomes():
    planets = []
    planets.append(genPlanet(FRIENDLY_HOME_N,
                             FRIENDLY_USER_N, 100, -180, 0, 100, 24))
    planets.append(genPlanet(ENEMY_HOME_N, ENEMY_USER_N, 100, 180, 0, 100, 24))
    return planets
