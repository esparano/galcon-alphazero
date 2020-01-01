import pickle
import time

from nn.config import GAME_SOURCE_DIR


def loadTrainingGame(filename):
    with open(filename, 'rb') as fp:
        return pickle.load(fp)


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
        saveGameFileName = f"{GAME_SOURCE_DIR}/game_{time.time()}_{userN}.pickle"
        with open(saveGameFileName, 'wb') as fp:
            pickle.dump(self, fp)
