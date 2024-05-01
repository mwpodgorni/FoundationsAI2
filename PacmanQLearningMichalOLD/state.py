import numpy as np
from run import GameController
import random
import math
from constants import *
from vector import Vector2
BOARD_ROWS = 29
BOARD_COLS = 26
# Data structure for holding information about the current state
# of the game, as well as for progressing the learning.
class State:
    def __init__(self):
        # print('nodes', nodes.getListOfNodesVector())
        # print('pellets', pellets.pelletList)
        self.board = {}
        print('board', self.board)
        self.isEnd = False
        self.gridHash = None
        self.game = None
        self.range_limit = 5
        self.pacmanSymbol = 5
        # pellet = 1
        # powerPellet = 2
        # ghost = 3
        # scaredGhost = 4
        # pacman = 5
        # empty = 0

    def getHash(self):

        self.boardHash = str(self.board.reshape(BOARD_COLS * BOARD_ROWS))
        return self.boardHash
    def setupBoard(self):
        pacman_node = self.game.pacman.node.position
        pacman_node = (pacman_node.x, pacman_node.y)
        print('pacman_node', pacman_node)
        # Define the range to consider around Pacman's node
        # Loop over the nodes within the specified range around Pacman along both axes
        for node in self.game.nodes.getListOfNodesVector():
            # print('node', node)
            if abs(node[0] - pacman_node[0]) <= self.range_limit * TILEWIDTH and abs(node[1] - pacman_node[1]) <= self.range_limit * TILEHEIGHT:
                self.board[(node[0], node[1])] = self.getNodeSymbol(node)

        print ('setup board', self.board)
        print ('setup board values', self.board.values())
        # for node in self.game.nodes.getListOfNodesVector():
        #     self.board[(node[0],node[1])] =0
        # print ('setup board', self.board)
        # print ('setup board values', self.board.values())

    def updateState(self, position):
                # Clear the board before updating
        self.board = {}

        pacman_node = self.game.pacman.node.position
        pacman_node = (pacman_node.x, pacman_node.y)

        # Define the range to consider around Pacman's node

        # Loop over the nodes within the specified range around Pacman
        for node in self.game.nodes.getListOfNodesVector():
            if abs(node[0] - pacman_node[0]) <= self.range_limit* TILEWIDTH and abs(node[1] - pacman_node[1]) <= self.range_limit* TILEHEIGHT:
                self.board[(node[0], node[1])] = self.getNodeSymbol(node)
        # nodes = self.game.nodes.getListOfNodesVector()
        # # print('nodes', nodes)
        # for node in self.game.nodes.getListOfNodesVector():
        #     self.board[(node[0],node[1])] = self.getNodeSymbol(node)
        print('board', self.board.values())
        # print('board', self.board)

    def getNodeSymbol(self, node):
        ghostDanger = self.getGhostsTargets([SCATTER, CHASE])
        ghostScared = self.getGhostsTargets([FREIGHT])
        pacmanNode = (self.game.pacman.node.position.x, self.game.pacman.node.position.y)
        pellets = [(p.position.x, p.position.y) for p in self.game.pellets.pelletList]
        powerPellets = [(p.position.x, p.position.y) for p in self.game.pellets.powerpellets]
        # print('=======================')
        if pacmanNode == node:
            return 5
        if node in ghostDanger:
            return 3
        if node in ghostScared:
            return 4
        if node in powerPellets:
            return 2
        if node in pellets:
            return 1
        return 0

    def getGhostsTargets(self, states):
        ghosts = []
        for ghost in self.game.ghosts:
            if  ghost.mode.current in states:
                ghosts.append((int(ghost.node.position.x), int(ghost.node.position.y)))
        return ghosts

    def play(self,iterations = 10):
        for i in range(iterations):
            if i % 10 == 0:
                print("Iterations: ", i)
            self.game =  GameController()
            self.game.startGame()
            self.setupBoard()
            while not self.game.isEnd:
                if(self.game.pacman.nextMove):
                    self.game.pacman.nextMove = False
                    print('hello')
                    # rand_nu = random.uniform(0,1)
                    # if rand_nu < self.p1.walk_len_nu:
                        # self.board = self.game.pacman.randomDirection()

                    positions = self.game.pacman.validDirections()
                    # # Explore: select a random action with a probability of rand_rho...
                    rand_rho = random.uniform(0,1)
                    if rand_rho < self.game.pacman.exploration_rho:
                        # take random action
                        idx = np.random.choice(len(positions))
                        p1_action = positions[idx]
                    # # Exploit: else, take the best action for the current state-action pair.
                    else:
                        p1_action = self.game.pacman.chooseAction(positions, self.board, self.pacmanSymbol)
                    # # Apply the action and update board state.
                    self.updateState(p1_action)
                    board_hash = self.getHash()
                    self.p1.addState(board_hash)
                self.game.update()

    def giveReward(self):
        isOver = self.isEnd()
        if isOver:
            if self.pacmanWon():
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
    def pacmanWon(self):
        return self.game.pacman.alive

    def getNearestNode(self, position):
            print(f'getNearestNode:{position}')
            min_distance = float('inf')
            nearest_node = None
            if isinstance(position, Vector2):
                position = (position.x, position.y)
            for node_position in self.game.nodes.nodesLUT.keys():
                distance = math.sqrt((position[0] - node_position[0])**2 + (position[1] - node_position[1])**2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_node = self.game.nodes.nodesLUT[node_position]
            return nearest_node

if __name__ == "__main__":
    s = State()
    s.play(1)
