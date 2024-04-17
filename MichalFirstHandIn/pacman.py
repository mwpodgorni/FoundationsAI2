import pygame
from pygame.locals import *
from constants import *
from entity import Entity
from sprites import PacmanSprites
from algorithms import dijkstra_or_a_star
from random import choice
import random

class Pacman(Entity):
    def __init__(self, node):
        Entity.__init__(self, node )
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        # 
        # added fields
        # 
        # ghost reference
        self.ghosts = None
        # nodes reference
        self.nodes=None
        # current pacman state
        self.myState=None
        # direction method (changes based on state)
        self.directionMethod = self.goalDirection
        # pellets left to collect
        self.leftoverPellets = []
        # if ghost is closer than specified distance, pacman will go into RUN_AWAY state
        self.ghostTooCloseThreshold = 5000
        # if freight ghost is closer than specified distance, pacman will go into SEEK_GHOST state
        self.seekGhostThreshold = 3000


    def getGhosts(self, ghost):
        self.ghosts = ghost
    def getNodes(self, nodes):
        self.nodes=nodes
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
        self.position += self.directions[self.direction]*self.speed*dt

        # update pacman's state
        self.updateState()
        # update pacman's goal
        self.updateGoal()
        # update pacman's position
        self.updatePosition()
    
    # update pacman state
    # priority: RUN_AWAY > SEEK_GHOST > SEEK_PELLET
    def updateState(self):
        nearestDangerGhost = self.getNearestGhost([SCATTER, CHASE])
        # if ghost found, get distance, if not set it to threshold +1
        nearestDangerGhostDistance = (nearestDangerGhost.position - self.position).magnitudeSquared() if nearestDangerGhost is not None else self.ghostTooCloseThreshold+1
        
        nearestFreightenedGhost = self.getNearestGhost([FREIGHT])
        # if ghost found, get distance, if not set it to threshold +1
        nearestFreightenedGhostDistance = (nearestFreightenedGhost.position - self.position).magnitudeSquared() if nearestFreightenedGhost is not None else self.seekGhostThreshold+1

        # update states in order based on current situation
        if nearestDangerGhostDistance < self.ghostTooCloseThreshold:
            self.myState = RUN_AWAY
            self.directionMethod = self.getRunAwayDirection
        elif nearestFreightenedGhostDistance < self.seekGhostThreshold:
            self.myState = SEEK_GHOST
            self.directionMethod = self.goalDirection
        else:
            self.myState = SEEK_PELLET
            self.directionMethod = self.goalDirection
    
    # update goal based on current state
    def updateGoal(self):
        if self.myState == SEEK_PELLET:
            self.goal = self.getNewNearestPellet()
        if self.myState == RUN_AWAY:
            self.goal = self.getNearestGhost([SCATTER, CHASE]).target.position
        if self.myState == SEEK_GHOST:
            self.goal = self.getNearestGhost([FREIGHT]).target.position
    
    # update pacman's position
    def updatePosition(self):
        if self.overshotTarget():
            self.node = self.target
            directions = self.getValidDirections()
            direction = self.directionMethod(directions)
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)
            self.setPosition()
    
    def getValidDirections(self):
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.isValidDirection(key):
                directions.append(key)
        if len(directions) == 0:
            directions.append(self.direction)
        return directions
    
    def isValidDirection(self, direction):
        if direction is not STOP:
            if self.node.neighbors[direction] is not None:
                return True
        return False
    
    # get pellet that is closed to the current pacman position
    def getNewNearestPellet(self):
        nearest_pellet = None
        nearest_distance_squared = float('inf')
        pacman_position = self.position
        for pellet in self.leftoverPellets:
            pellet_position = pellet.position
            distance_squared = (pellet_position - pacman_position).magnitudeSquared()
            if distance_squared < nearest_distance_squared:
                nearest_distance_squared = distance_squared
                nearest_pellet = pellet
        return nearest_pellet.position
    
    # get direction towards which pacman should run away from a ghost
    # slightly biased to running away to sides, rather than straight
    def getRunAwayDirection(self, directions):
        distances = []
        if random.random() < 0.6:
            if self.direction in [LEFT, RIGHT]:
                if UP in directions:
                    return choice([UP, DOWN]) if DOWN in directions else UP
                elif DOWN in directions:
                    return DOWN
            elif self.direction in [UP, DOWN]:
                if LEFT in directions:
                    return choice([LEFT, RIGHT]) if RIGHT in directions else LEFT
                elif RIGHT in directions:
                    return RIGHT
        for direction in directions:
            vec = self.node.position  + self.directions[direction]*TILEWIDTH - self.goal
            distances.append(vec.magnitudeSquared())
        index = distances.index(max(distances))
        return directions[index]
    
    # get nearest ghost with one of the provided states
    def getNearestGhost(self, states):
        smallest_distance = float('inf')
        nearest_ghost = None
        for ghost in self.ghosts:
            distance = (ghost.position - self.position).magnitudeSquared()
            if ghost.mode.current in states and distance < smallest_distance:
                smallest_distance = distance
                nearest_ghost = ghost
        return nearest_ghost 

    def eatPellets(self, pelletList):
        self.leftoverPellets = pelletList
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

    # Chooses direction in which to turn based on the a*
    def goalDirection(self, directions):
        path = self.getAStarPath()
        pacmanTarget = self.target
        pacmanTarget = self.nodes.getVectorFromLUTNode(pacmanTarget)
        path.append(pacmanTarget)
        if len(path) == 1:
            return choice(directions)
        nextPacmanNode = path[1]
        if pacmanTarget[0] > nextPacmanNode[0] and 2 in directions : #left
            return 2
        if pacmanTarget[0] < nextPacmanNode[0] and -2 in directions : #right
            return -2
        if pacmanTarget[1] > nextPacmanNode[1] and 1 in directions : #up
            return 1
        if pacmanTarget[1] < nextPacmanNode[1] and -1 in directions : #down
            return -1
        else:
            return choice(directions)

    #############
    # Executes A* from pacman's target as start to pacman's goal.
    def getAStarPath(self):
        if self.goal is None:
            return []
        lastPacmanNode = (self.goal.x, self.goal.y)
        pacmanTarget = self.target
        pacmanTarget = self.nodes.getVectorFromLUTNode(pacmanTarget)

        previous_nodes, shortest_path = dijkstra_or_a_star(self.nodes, pacmanTarget, a_star=True)
        path = []
        node = lastPacmanNode
        while node != pacmanTarget:
            path.append(node)
            if node in previous_nodes:
                node = previous_nodes[node]
            else:
                break
        path.append(pacmanTarget)
        path.reverse()
        return path