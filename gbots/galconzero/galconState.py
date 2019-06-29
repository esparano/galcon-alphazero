from log import log
from gz_mathutils import getVectorComponents, angle
from models import Item
from stateSim import simulate
from actions import SEND_ACTION, REDIRECT_ACTION, NULL_ACTION


NEW_FLEET_N = 10000


class GalconState():

    # actionGen and evaluator are injected
    def __init__(self, items, playerN, enemyN, actionGen, evaluator):
        self.items = items
        self.playerN = playerN
        self.enemyN = enemyN
        self.actionGen = actionGen
        self.evaluator = evaluator
        # TODO: expand and calculate both reward and possible actions simultaneously?
        # Then mark node as expanded and store results

    def getPriorProbabilities(self):
        actions = self.actionGen.getPriorProbabilities(
            self.items, self.playerN, self.enemyN)
        assert sum(
            action[0] for action in actions) == 1, "prior probabilities did not add to 1. Sum was :1?"
        return actions

    def takeAction(self, action):
        # TODO: this can be heavily optimized. a map object could store static data like planet x,y,prod, and nodes
        # could contain deltas from parent states instead of an entirely new copy of the map?
        itemDictCopy = {k: self.items[k].getCopy() for k in self.items}
        newState = GalconState(itemDictCopy, self.enemyN,
                               self.playerN, self.actionGen, self.evaluator)

        if action[1] == SEND_ACTION:
            newState.executeSend(action)
        elif action[1] == REDIRECT_ACTION:
            newState.executeRedirect(action)

        # TODO: don't simulate forward if owner is not the bot - simultaneous turns??
        # TODO: go back to default timestep
        simulate(newState.items, 10)

        return newState

    # TODO: test this
    def executeSend(self, sendAction):
        (_, _, sourceN, targetN, perc) = sendAction
        source = self.items[sourceN]
        target = self.items[targetN]

        # TODO: min 1 ship, rounding? etc.
        numToSend = source.ships * perc / 100
        if (numToSend > source.ships):
            log("WARNING: attempting to send {} when planet has {}".format(
                numToSend, source.ships))
            numToSend = source.ships

        source.ships -= numToSend
        assert source.ships >= 0, "source.ships {} < 0".format(source.ships)

        (xSpawnOffset, ySpawnOffset) = getVectorComponents(
            angle(source, target), source.radius)

        global NEW_FLEET_N
        createdFleet = Item(
            n=NEW_FLEET_N,
            type="fleet",
            owner=source.owner,
            ships=numToSend,
            x=source.x + xSpawnOffset,
            y=source.y + ySpawnOffset,
            source=sourceN,
            target=targetN,
            radius=5,  # TODO: fleet radius estimation/update
            xid=NEW_FLEET_N,  # TODO: what is this?
        )

        # TODO: make sure this doesn't overwrite an object?
        # Is it even possible for it to overwrite an object?
        print("adding to items {}".format(createdFleet.n))
        self.items[createdFleet.n] = createdFleet

        NEW_FLEET_N += 1

    # TODO: test this
    def executeRedirect(self, redirectAction):
        (_, _, sourceN, targetN) = redirectAction
        source = self.items[sourceN]
        source.target = targetN

    # TODO:
    def isTerminal(self):
        return False

    def getReward(self):
        return self.evaluator.getEval(self.items, self.playerN, self.enemyN)
