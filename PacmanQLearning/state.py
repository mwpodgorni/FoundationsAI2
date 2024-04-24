import numpy as np
from run import GameController
# Data structure for holding information about the current state
# of the game, as well as for progressing the learning.
class State:
    def __init__(self):
        # print('nodes', nodes.getListOfNodesVector())
        # print('pellets', pellets.pelletList)
        self.isEnd = False
        self.gridHash = None
        self.game = None

    def play(self,iterations = 10):
        for i in range(iterations):
            if i % 10 == 0:
                print("Iterations: ", i)
            self.game =  GameController()
            self.game.startGame()
            while not self.game.isEnd:
                self.game.update()


if __name__ == "__main__":
    s = State()
    s.play(1)