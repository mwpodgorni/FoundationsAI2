import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
import random
class Pacman(Entity):
    def __init__(self, node, exploration_rho=0.3, lr_alpha=0.2, discount_rate_gamma=0.9, walk_len_nu=0.2):
        Entity.__init__(self, node )
        self.name = PACMAN
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.nextMove = False
        # Q-Learning parameters
        self.exploration_rho = exploration_rho
        self.lr_alpha = lr_alpha
        self.discount_rate_gamma = discount_rate_gamma
        self.walk_len_nu = walk_len_nu

    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    def die(self):
        self.alive = False
        self.direction = STOP

    def update(self, dt):
        self.sprites.update(dt)
        # print('position', self.position)
        # print('direction', self.direction)
        # print('direction2', self.directions[self.direction])
        self.position += self.directions[self.direction]*self.speed*dt
        direction = self.getValidKey()
        # direction = self.learningDirection
        # print('after', direction)
        if self.overshotTarget():
            self.node = self.target
            self.nextMove = True
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                # check iif this is good
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        else:
            if self.oppositeDirection(direction):
                self.reverseDirection()

    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
                return pellet
        return None

    def collideGhost(self, ghost):
        return self.collideCheck(ghost)

    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False

    def chooseAction(self, positions, current_board, symbol):
        value_max = -999
        duplicates = []
        # Find the position that will give the best value by
        # iteratively checking each available position's value
        # if the player was to take that position.
        for position in positions:
            next_board = current_board.copy()
            next_board[position] = symbol
            next_boardHash = self.getHash(next_board)
            if self.states_value.get(next_boardHash) is None:
                value = 0
            else:
                value = self.states_value.get(next_boardHash)
            # print("value", value)
            if value > value_max:
                value_max = value
                action = position
                duplicates = []
                duplicates.append(action)
            if value == value_max:
                duplicates.append(position)
        # if there are multiple max values, pick one randomly
        if len(duplicates)> 1:
            return random.choice(duplicates)
        # else, just pick the highest action
        else:
            return action
