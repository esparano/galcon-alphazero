import random


def getPlanets(items):
    return [p for p in items.values() if p.type == 'planet']


class EvalAndMoveGen:
    # TODO: prior probabilities
    def getPossibleActions(self, items, playerN, enemyN):
        planets = getPlanets(items)
        myPlanets = [p for p in planets if p.owner == playerN]
        otherPlanets = [p for p in planets if p.owner != playerN]
        return [(
            random.choice(myPlanets).n,
            random.choice(otherPlanets).n,
            random.randrange(5, 100, 5)
        ) for _ in range(5)]

    def getEval(self, items, playerN, enemyN):
        planets = getPlanets(items)
        myPlanets = [p for p in planets if p.owner == playerN]
        enemyPlanets = [p for p in planets if p.owner != enemyN]
        myProd = sum(p.production for p in myPlanets)
        enemyProd = sum(p.production for p in enemyPlanets)
        return myProd - enemyProd
