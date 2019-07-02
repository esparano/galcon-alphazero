import pickle
import time
from log import log

DEFAULT_FILENAME = 'game_{}_{}.pickle'


class TrainingGame():
    def __init__(self):
        self.states = []
        self.refinedProbs = []
        # TODO: later on train against both Z and Q instead of just Z?
        self.result = None
        self.userN = None

    def appendState(self, state, refinedProb):
        self.states.append(state)
        self.refinedProbs.append(refinedProb)

    def saveGame(self, userN, result):
        self.userN = userN
        self.result = result
        log("RESULT: {}".format(result))
        with open(DEFAULT_FILENAME.format(time.time(), userN), 'wb') as fp:
            pickle.dump(self, fp)
