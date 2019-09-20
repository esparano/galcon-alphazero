import math
from log import log
from gz_mathutils import vectorComponents
from models import Item
from stateSim import simulate
from actions import SendAction, RedirectAction, NullAction
from nnSetup import NUM_ACTIONS_PER_LAYER

NEW_FLEET_N = 10000


class GalconState():

    # actionGen and evaluator are injected
    def __init__(self, items, playerN, enemyN, mapHelper):
        self.items = items
        self.playerN = playerN
        self.enemyN = enemyN
        self.mapHelper = mapHelper
        # TODO: expand and calculate both reward and possible actions simultaneously?
        # Then mark node as expanded and store results

    def mapActionIndexToAction(self, actionIndex):
        if actionIndex == 0:
            return NullAction()
        elif actionIndex <= NUM_ACTIONS_PER_LAYER:
            sourceN, targetN = self.mapHelper.indexToSourceTargetN(actionIndex)
            return SendAction(sourceN, targetN, 50)
        else:
            assert False, "Redirect is not yet supported"
            # newState.executeRedirect(action)

    def takeAction(self, actionIndex):
        # TODO: this can be heavily optimized. a map object could store static data like planet x,y,prod, and nodes
        # could contain deltas from parent states instead of an entirely new copy of the map?
        itemDictCopy = {k: self.items[k].getCopy() for k in self.items}
        newState = GalconState(itemDictCopy, self.enemyN,
                               self.playerN, self.mapHelper)

        chosenAction = self.mapActionIndexToAction(actionIndex)
        # TODO: FIX THIS RUNTIME ERROR using mapHelper
        if isinstance(chosenAction, NullAction):
            # null action
            pass
        elif isinstance(chosenAction, SendAction):
            newState.executeSend(chosenAction)
        else:
            assert False, "Redirect is not yet supported"
            # newState.executeRedirect(action)

        # TODO: don't simulate forward if owner is not the bot - simultaneous turns??
        # TODO: go back to default timestep
        simulate(newState.items, 0.5)

        return newState

    # TODO: test this
    def executeSend(self, sendAction):
        source = self.items[sendAction.sourceN]
        target = self.items[sendAction.targetN]
        perc = sendAction.percent

        # TODO: min 1 ship, rounding? etc.
        numToSend = source.ships * (perc / 100)
        if (numToSend > source.ships):
            log("WARNING: attempting to send {} when planet has {}".format(
                numToSend, source.ships))
            numToSend = source.ships

        source.ships -= numToSend
        assert source.ships >= 0, "source.ships {} < 0".format(source.ships)

        (xSpawnOffset, ySpawnOffset) = vectorComponents(
            source.x, source.y, target.x, target.y, source.radius)

        global NEW_FLEET_N
        createdFleet = Item(
            n=NEW_FLEET_N,
            type="fleet",
            owner=source.owner,
            ships=numToSend,
            x=source.x + xSpawnOffset,
            y=source.y + ySpawnOffset,
            source=source.n,
            target=target.n,
            radius=5/100  # TODO: fleet radius estimation/update
        )

        # TODO: make sure this doesn't overwrite an object?
        # Is it even possible for it to overwrite an object?
        self.items[createdFleet.n] = createdFleet

        NEW_FLEET_N += 1

    # TODO: test this
    def executeRedirect(self, redirectAction):
        fleet = self.items[redirectAction.sourceN]
        fleet.target = redirectAction.targetN

    # TODO: calculate terminal states
    # It's possible that trying to determine terminal states will just cost more time than a search?
    # If a terminal state is nearby, the game is basically over anyway?
    def isTerminal(self):
        return False
