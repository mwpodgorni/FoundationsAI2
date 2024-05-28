from __future__ import annotations

# avoiding circular dependency
from random import choice
from typing import TYPE_CHECKING, Any

import pygame

from algorithms import dijkstra_or_a_star
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
        self.directions = [UP, DOWN, LEFT, RIGHT]
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.learntDirection = LEFT
        self.ghostUp = False
        self.ghostDown = False
        self.ghostLeft = False
        self.ghostRight = False

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
        self.position += self.directions[self.direction] * self.speed * dt
        direction = int(self.learntDirection)
        if self.overshotTarget():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
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

    #############
    # Executes Dijkstra from Ghost's previous node as start 
    # to pacman's target node as target.
    def getDijkstraPath(self, direction, nodes, pellets):
        goal = self.getNearestPellet(pellets)
        goal = (goal.position.x, goal.position.y)
        currentNode = self.node
        currentNode = nodes.getNodeFromPixels(currentNode.position.x, currentNode.position.y)

        # previous_nodes, shortest_path = dijkstra(self.nodes, currentNode)
        previous_nodes, shortest_path = dijkstra_or_a_star(nodes, currentNode, a_star=True)
        path = []
        node = goal
        while node != currentNode:
            path.append(node)
            if node in previous_nodes:
                node = previous_nodes[node]
            else:
                break
        path.append(currentNode)
        path.reverse()
        # print(path)
        return path
    
    # Chooses direction in which to turn based on the dijkstra
    # returned path
    def goalDirectionDij(self, directions, nodes, pellets):
        path = self.getDijkstraPath(directions, nodes, pellets)
        currentNode = self.node
        currentNode = nodes.getPixelsFromNode(currentNode)
        path.append(currentNode)
        nextNode = path[1]

        if currentNode[0] > nextNode[0] and 2 in directions : #left
            return 2
        if currentNode[0] < nextNode[0] and -2 in directions : #right
            return -2
        if currentNode[1] > nextNode[1] and 1 in directions : #up
            return 1
        if currentNode[1] < nextNode[1] and -1 in directions : #down
            return -1
        else:
            if -1 * self.direction in directions:
                return -1 * self.direction
            else:
                return choice(directions)
        # up 1, down -1, left 2, right -2

    # Seeks the nearest pellet
    def getNearestPellet(self, pellets):
        shortestDistance = float('inf')
        nearestPellet = None
        
        for pellet in pellets:
            # Measure the Distance between this pellet and Pacman
            distance = (pellet.position - self.position).magnitudeSquared()

            # If this pellet is closer than any other distances known
            # then choose this as the currently nearest pellet.
            if distance < shortestDistance :
                shortestDistance = distance
                nearestPellet = pellet

        return nearestPellet

    def getNodesInDirection(self, direction, amount):
        nodes = []
        node = self.node
        prevDir = direction

        for i in range(0, amount - 1):
            nextNode = node.neighbors[prevDir]
            
            if i == 0 and nextNode == None :
                break

            if nextNode != None:
                nodeInDirection = nextNode       
                nodes.append(nodeInDirection)
                node = nodeInDirection
            else:
                node, prevDir = self.getAnyNeighborNode(node, prevDir)
                nodes.append(node)           
            
        return nodes
    
    def getAnyNeighborNode(self, node, prevDir):
        for direction in [UP, DOWN, LEFT, RIGHT]:
            if prevDir != direction:
                neighbor = node.neighbors[direction]
                return neighbor, direction
    
    def checkGhostInNodes(self, direction, ghosts):
        if ghosts != None :
            nodes = self.getNodesInDirection(direction, 5)
    
            if len(nodes) != 0:
                for node in nodes :
                    for ghost in ghosts:
                        if ghost.target == node : 
                            return True
                return False
        else:
            print("No Ghosts")
            return False

    def validDirections(self):
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.validDirection(key):
                directions.append(key)
        if len(directions) == 0:
            directions.append(self.direction * -1)
        return directions