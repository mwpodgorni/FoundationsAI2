import numpy as np
from run import GameController
import random
BOARD_ROWS = 29
BOARD_COLS = 26
# Data structure for holding information about the current state
# of the game, as well as for progressing the learning.
class State:
    def __init__(self):
        # print('nodes', nodes.getListOfNodesVector())
        # print('pellets', pellets.pelletList)
        self.board = np.zeros((BOARD_ROWS, BOARD_COLS))
        print('bpard', self.board)
        self.isEnd = False
        self.gridHash = None
        self.game = None
        # pellet = .
        # powerPellet = +
        # ghost = g 
        # pacman = p
        # empty = 0
        # scaredGhost = s
    def getHash(self):
        self.boardHash = str(self.board.reshape(BOARD_COLS * BOARD_ROWS))
        return self.boardHash
    def updateState(self, position):
        nodes = self.game.nodes.getListOfNodesVector()
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                self.board[i,j] = self.getNodeSymbol(nodes[i+j]) 
        print('board', self.board)

    def getNodeSymbol(self, node):
        ghosts = self.game.ghosts
        ghostDanger =
        ghostScared = 
        pacman = self.game.pacman.position
        pellets = self.game.pellets.pelletList
        powerPellets = self.game.pellets.powerPelletList

                    
    def play(self,iterations = 10):
        for i in range(iterations):
            if i % 10 == 0:
                print("Iterations: ", i)
            self.game =  GameController()
            self.game.startGame()
            while not self.game.isEnd:
                print('hello')
                # rand_nu = random.uniform(0,1)
                # if rand_nu < self.p1.walk_len_nu:
                #     self.board = self.game.pacman.randomDirection()

                # positions = self.game.pacman.validDirections()
                # # Explore: select a random action with a probability of rand_rho...
                # rand_rho = random.uniform(0,1)
                # if rand_rho < self.p1.exploration_rho:
                #     # take random action
                #     idx = np.random.choice(len(positions))
                #     p1_action = positions[idx]
                # # Exploit: else, take the best action for the current state-action pair.
                # else:
                #     p1_action = self.game.pacman.chooseAction(positions, self.board, self.playerSymbol)
                # # Apply the action and update board state.
                self.updateState('fuck')
                # board_hash = self.getHash()
                # self.p1.addState(board_hash)
                self.game.update()

    def giveReward(self):
        isOver = self.isEnd()
        if isOver:
            if self.winner():
                self.p1.feedReward(1)
            else:
                self.p1.feedReward(-1)
        else:
            if self.ateGhost():
                self.p1.feedReward(0.5)
            elif self.atePowerPellet():
                self.p1.feedReward(0.3)
            elif self.atePellet():
                self.p1.feedReward(0.2)
            else:
                self.p1.feedReward(0)


if __name__ == "__main__":
    s = State()
    s.play(1)