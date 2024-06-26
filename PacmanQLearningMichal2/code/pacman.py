from __future__ import annotations

# avoiding circular dependency
from typing import TYPE_CHECKING, Any

import pygame

from constants import DOWN, LEFT, PACMAN, PORTAL, RIGHT, STOP, UP, YELLOW
from entity import Entity
from sprites import PacmanSprites


class Pacman(Entity):
    def __init__(self, node):
        Entity.__init__(self, node)
        self.name = PACMAN
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.learntDirection = LEFT
        self.lastNode = node


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
        print("UDPATRE PACMAN", self.position.x, self.position.y)
        self.sprites.update(dt)

        self.position += self.directions[self.direction] * self.speed * dt
        if self.overshotTarget():
            print('OVRESHOT TARGET')
            # print("LEARNT DIRECTION", self.learntDirection)
            # print("self.direction", self.direction)
            self.node = self.target
            direction = self.learntDirection
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            # print('TARGET', self.target.position.x, self.target.position.y)
            # print('NODE', self.node.position.x, self.node.position.y)
            if self.target is not self.node:
                # print("SETTING DIRECTION", direction)
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)
            self.setPosition()
        # else:
        #     if self.oppositeDirection(direction):
        #         self.reverseDirection()
    def getNewTarget(self, direction):
        if self.validDirection(direction):
            # print('new target if')
            return self.node.neighbors[direction]
        # print('new target else')
        return self.node
    def validDirections(self):
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.validDirection(key):
                if key != self.direction * -1:
                    directions.append(key)
        if len(directions) == 0:
            directions.append(self.direction * -1)
        return directions

    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_UP]:
            return UP
        if key_pressed[pygame.K_DOWN]:
            return DOWN
        if key_pressed[pygame.K_LEFT]:
            return LEFT
        if key_pressed[pygame.K_RIGHT]:
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
        rSquared = (self.collideRadius + other.collideRadius) ** 2
        if dSquared <= rSquared:
            return True
        return False
