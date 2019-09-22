from gz_mathutils import futureShips, timeToDist, vectorComponents, dist
from log import log


# TODO: gradual fleet landing
# land the fleet, even if it's far away


def forceLandFleet(items, fleet):
    target = items[fleet.target]

    # update ships as fleet lands on planet
    if fleet.owner == target.owner:
        target.ships += fleet.ships
    else:
        diff = target.ships - fleet.ships
        if diff < 0:
            # change ownership
            target.ships = -diff
            target.owner = fleet.owner
            target.neutral = False
        else:
            target.ships = diff

    del items[fleet.n]


def simulate(items, timestep=0.25):
    if timestep == 0:
        return

    # first, add production
    for p in items.values():
        # TODO: optimize!!
        if p.type == 'planet':
            p.ships = futureShips(p.neutral, p.ships, p.production, timestep)

    # second, move fleets towards goal.
    # TODO: It's possible to figure out WHEN the fleet actually lands
    # if it lands somewhere between timesteps, then
    # adjust production and capturing more accurately. But it's irrelevant
    # for small enough timestep

    fleetUpdateDist = timeToDist(timestep)
    for f in list(items.values()):
        # TODO: optimize!!
        if f.type == 'fleet':
            target = items[f.target]
            fDist = dist(f.x, f.y, target.x, target.y)
            # TODO: add 1 ship radius?
            if fDist - fleetUpdateDist < target.radius:
                forceLandFleet(items, f)
            else:
                (xDelta, yDelta) = vectorComponents(
                    f.x, f.y, target.x, target.y, fleetUpdateDist)
                f.x += xDelta
                f.y += yDelta

    # TODO: fleet radius changing with fleets getting stuck on neutrals
    # TODO: planets settle, fleets settle
