from __future__ import annotations

# avoiding circular dependency
from typing import TYPE_CHECKING, Any
import pygame
from nodes import Node
from constants import (
    BLACK,
    FREIGHT,
    GAMEOVERTXT,
    LEFT,
    PAUSETXT,
    POWERPELLET,
    READYTXT,
    RIGHT,
    SCREENHEIGHT,
    SCREENSIZE,
    SCREENWIDTH,
    SPAWN,
    WHITE,
)
from pacman import Pacman
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import GhostGroup
from fruit import Fruit
from pauser import Pause
from text import TextGroup
from sprites import LifeSprites
from sprites import MazeSprites
from mazedata import MazeData
from constants import *

class GameController(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.clock = pygame.time.Clock()
        self.fruit = None
        self.pause = Pause(False)
        self.level = 0
        self.lives = 5
        self.score = 0
        self.textgroup = TextGroup()
        self.lifesprites = LifeSprites(self.lives)
        self.flashBG = False
        self.flashTime = 0.2
        self.flashTimer = 0
        self.fruitCaptured = []
        self.fruitNode = None
        self.mazedata = MazeData()  ######
        self.range_limit = 5
        self.lastPacmanMove = None

    def setBackground(self):
        self.background_norm = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_norm.fill(BLACK)
        self.background_flash = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_flash.fill(BLACK)
        self.background_norm = self.mazesprites.constructBackground(
            self.background_norm, self.level % 5
        )
        self.background_flash = self.mazesprites.constructBackground(
            self.background_flash, 5
        )
        self.flashBG = False
        self.background = self.background_norm

    def startGame(self):
        self.mazedata.loadMaze(self.level)
        assert self.mazedata.obj is not None
        self.mazesprites = MazeSprites(
            self.mazedata.obj.name + ".txt", self.mazedata.obj.name + "_rotation.txt"
        )
        self.setBackground()
        self.nodes = NodeGroup(self.mazedata.obj.name + ".txt")
        self.mazedata.obj.setPortalPairs(self.nodes)
        self.mazedata.obj.connectHomeNodes(self.nodes)
        self.pacman = Pacman(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.pacmanStart)
        )
        self.pellets = PelletGroup(self.mazedata.obj.name + ".txt")
        self.ghosts = GhostGroup(self.nodes.getStartTempNode(), self.pacman)

        self.ghosts.pinky.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3))
        )
        self.ghosts.inky.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(0, 3))
        )
        self.ghosts.clyde.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(4, 3))
        )
        self.ghosts.setSpawnNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3))
        )
        self.ghosts.blinky.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 0))
        )

        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.mazedata.obj.denyGhostsAccess(self.ghosts, self.nodes)

    def startGameRandom(self):
        self.mazedata.loadMaze(self.level)
        assert self.mazedata.obj is not None
        self.mazesprites = MazeSprites(
            self.mazedata.obj.name + ".txt", self.mazedata.obj.name + "_rotation.txt"
        )
        self.setBackground()
        self.nodes = NodeGroup(self.mazedata.obj.name + ".txt")
        self.mazedata.obj.setPortalPairs(self.nodes)
        self.mazedata.obj.connectHomeNodes(self.nodes)

        self.setPacmanInRandomPosition()
        self.pellets = PelletGroup(self.mazedata.obj.name + ".txt")
        self.ghosts = GhostGroup(self.nodes.getStartTempNode(), self.pacman)

        self.ghosts.pinky.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3))
        )
        self.ghosts.inky.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(0, 3))
        )
        self.ghosts.clyde.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(4, 3))
        )
        self.ghosts.setSpawnNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3))
        )
        self.ghosts.blinky.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 0))
        )

        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.mazedata.obj.denyGhostsAccess(self.ghosts, self.nodes)

    def update(self):
        TIMESCALE = 2.0

        # dt = self.clock.tick(30) / 1000.0
        dt = self.clock.tick(60) / 1000.0 * TIMESCALE
        self.textgroup.update(dt)
        self.pellets.update(dt)
        if not self.pause.paused:
            self.ghosts.update(dt)
            if self.fruit is not None:
                self.fruit.update(dt)
            if self.lastPacmanMove!='atePellet':
                self.lastPacmanMove = 'justMove'
            self.checkPelletEvents()
            self.checkGhostEvents()
            self.checkFruitEvents()

        if self.pacman.alive:
            if not self.pause.paused:
                self.pacman.update(dt)
        else:
            self.pacman.update(dt)

        if self.flashBG:
            self.flashTimer += dt
            if self.flashTimer >= self.flashTime:
                self.flashTimer = 0
                if self.background == self.background_norm:
                    self.background = self.background_flash
                else:
                    self.background = self.background_norm

        afterPauseMethod = self.pause.update(dt)
        if afterPauseMethod is not None:
            afterPauseMethod()
        self.checkEvents()
        self.render()

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.pacman.alive:
                        self.pause.setPause(playerPaused=True)
                        if not self.pause.paused:
                            self.textgroup.hideText()
                            self.showEntities()
                        else:
                            self.textgroup.showText(PAUSETXT)
                            # self.hideEntities()

    def checkPelletEvents(self):
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.lastPacmanMove = 'atePellet'
            self.pellets.numEaten += 1
            self.updateScore(pellet.points)
            if self.pellets.numEaten == 30:
                self.ghosts.inky.startNode.allowAccess(RIGHT, self.ghosts.inky)
            if self.pellets.numEaten == 70:
                self.ghosts.clyde.startNode.allowAccess(LEFT, self.ghosts.clyde)
            self.pellets.pelletList.remove(pellet)
            if pellet.name == POWERPELLET:
                self.lastPacmanMove = 'atePowerPellet'
                self.ghosts.startFreight()
            if self.pellets.isEmpty():
                self.flashBG = True
                self.hideEntities()
                self.pause.setPause(pauseTime=3, func=self.nextLevel)

    def checkGhostEvents(self):
        for ghost in self.ghosts:
            if self.pacman.collideGhost(ghost):
                if ghost.mode.current is FREIGHT:
                    self.lastPacmanMove = 'ateGhost'
                    self.pacman.visible = False
                    ghost.visible = False
                    self.updateScore(ghost.points)
                    self.textgroup.addText(
                        str(ghost.points),
                        WHITE,
                        ghost.position.x,
                        ghost.position.y,
                        8,
                        time=1,
                    )
                    self.ghosts.updatePoints()
                    self.pause.setPause(pauseTime=1, func=self.showEntities)
                    ghost.startSpawn()
                    self.nodes.allowHomeAccess(ghost)
                elif ghost.mode.current is not SPAWN:
                    self.lastPacmanMove = 'hitGhost'
                    if self.pacman.alive:
                        self.lives -= 1
                        self.lifesprites.removeImage()
                        self.pacman.die()
                        self.ghosts.hide()
                        if self.lives <= 0:
                            self.textgroup.showText(GAMEOVERTXT)
                            self.pause.setPause(
                                pauseTime=3, func=self.restartGameRandom
                            )
                        else:
                            self.pause.setPause(pauseTime=3, func=self.resetLevel)

    def checkFruitEvents(self):
        if self.pellets.numEaten == 50 or self.pellets.numEaten == 140:
            if self.fruit is None:
                self.fruit = Fruit(self.nodes.getNodeFromTiles(9, 20), self.level)
                print(self.fruit)
        if self.fruit is not None:
            if self.pacman.collideCheck(self.fruit):
                self.updateScore(self.fruit.points)
                self.textgroup.addText(
                    str(self.fruit.points),
                    WHITE,
                    self.fruit.position.x,
                    self.fruit.position.y,
                    8,
                    time=1,
                )
                fruitCaptured = False
                for fruit in self.fruitCaptured:
                    if fruit.get_offset() == self.fruit.image.get_offset():
                        fruitCaptured = True
                        break
                if not fruitCaptured:
                    self.fruitCaptured.append(self.fruit.image)
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None

    def showEntities(self):
        self.pacman.visible = True
        self.ghosts.show()

    def hideEntities(self):
        self.pacman.visible = False
        self.ghosts.hide()

    def nextLevel(self):
        self.showEntities()
        self.level += 1
        self.pause.paused = False
        self.startGameRandom()
        self.textgroup.updateLevel(self.level)

    def restartGame(self):
        self.lives = 5
        self.level = 0
        self.pause.paused = False
        self.fruit = None
        self.startGame()
        self.textgroup.hideText()
        self.score = 0
        self.textgroup.updateScore(self.score)
        self.textgroup.updateLevel(self.level)
        self.lifesprites.resetLives(self.lives)
        self.fruitCaptured = []

    def restartGameRandom(self):
        self.lives = 5
        self.level = 0
        self.pause.paused = False
        self.textgroup.hideText()

        self.fruit = None
        self.startGameRandom()
        self.score = 0
        self.textgroup.updateScore(self.score)
        self.textgroup.updateLevel(self.level)
        self.lifesprites.resetLives(self.lives)
        self.fruitCaptured = []

    def setPacmanInRandomPosition(self):
        homeNode: Node = self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3))

        self.pacman = Pacman(self.nodes.getRandomNodeAwayFrom(homeNode.position, 300.0))  # type: ignore

    def resetLevel(self):
        self.pause.paused = False
        self.pacman.reset()
        self.ghosts.reset()
        self.fruit = None

    def updateScore(self, points):
        self.score += points
        self.textgroup.updateScore(self.score)

    def render(self):
        self.screen.blit(self.background, (0, 0))
        # self.nodes.render(self.screen)
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render(self.screen)
        self.textgroup.render(self.screen)

        for i in range(len(self.lifesprites.images)):
            x = self.lifesprites.images[i].get_width() * i
            y = SCREENHEIGHT - self.lifesprites.images[i].get_height()
            self.screen.blit(self.lifesprites.images[i], (x, y))

        for i in range(len(self.fruitCaptured)):
            x = SCREENWIDTH - self.fruitCaptured[i].get_width() * (i + 1)
            y = SCREENHEIGHT - self.fruitCaptured[i].get_height()
            self.screen.blit(self.fruitCaptured[i], (x, y))

        pygame.display.update()


    def pacmanPosition(self):
        return (int(self.pacman.node.position.x), int(self.pacman.node.position.y))
    def getPellets(self):
        pellets = []
        pacman_node = self.pacman.node.position
        pacman_node = (pacman_node.x, pacman_node.y)
        for p in self.pellets.pelletList:
            if abs(p.position.x - pacman_node[0]) <= self.range_limit * TILEWIDTH and abs( p.position.y - pacman_node[1]) <= self.range_limit * TILEHEIGHT:
                pellets.append((p.position.x, p.position.y))
        return pellets
    def getPowerPellets(self):
        powerPellets = []
        pacman_node = self.pacman.node.position
        pacman_node = (pacman_node.x, pacman_node.y)
        for p in self.pellets.powerpellets:
            if abs(p.position.x - pacman_node[0]) <= self.range_limit * TILEWIDTH and abs( p.position.y - pacman_node[1]) <= self.range_limit * TILEHEIGHT:
                powerPellets.append((p.position.x, p.position.y))
        return powerPellets
    
    def nearestDangerGhost(self):
        # pacman_node = self.pacman.node.position
        # pacman_node = (pacman_node.x, pacman_node.y)
        # min_dist = 100000
        # nearest_ghost = None
        # for ghost in self.ghosts:
        #     if ghost.mode.current in [SCATTER, CHASE]:
        #         g_node = ghost.node.position
        #         dist = abs(g_node.x - pacman_node[0]) + abs( g_node.y - pacman_node[1])
        #         if dist < min_dist:
        #             min_dist = dist
        #             nearest_ghost = (int(ghost.node.position.x), int(ghost.node.position.y))
        # print('nearestDangerGhost', nearest_ghost)
        # return nearest_ghost
        return self.getNearestGhostDist([SCATTER, CHASE])
    def nearestDangerGhostDir(self):
        return self.getNearestGhostDir([SCATTER, CHASE])
    def dangerGhosts(self):
        return self.getGhostsTargets([SCATTER, CHASE])
    
    def scaredGhosts(self):
        return self.getGhostsTargets([FREIGHT])
    
    def getGhostsTargets(self, states):
        ghosts = []
        pacman_node = self.pacman.node.position
        pacman_node = (pacman_node.x, pacman_node.y)
        for ghost in self.ghosts:
            if  ghost.mode.current in states:
                g_node = ghost.node.position
                if abs(g_node.x - pacman_node[0]) <= self.range_limit * TILEWIDTH and abs( g_node.y - pacman_node[1]) <= self.range_limit * TILEHEIGHT:
                    ghosts.append((int(ghost.node.position.x), int(ghost.node.position.y)))
        return ghosts
    
    def getNearestGhostDist(self, states):
        smallest_distance = float('inf')
        nearest_ghost = None
        for ghost in self.ghosts:
            distance = (ghost.position - self.pacman.node.position).magnitudeSquared()
            if ghost.mode.current in states and distance < smallest_distance:
                smallest_distance = distance
                nearest_ghost = ghost
        # return nearest_ghost
        return round(smallest_distance) if smallest_distance!=float('inf') else smallest_distance
    
    def getNearestGhostDir(self, states):
        smallest_distance = float('inf')
        nearest_ghost = None
        for ghost in self.ghosts:
            distance = (ghost.position - self.pacman.node.position).magnitudeSquared()
            if ghost.mode.current in states and distance < smallest_distance:
                smallest_distance = distance
                nearest_ghost = ghost
        if nearest_ghost is None:
            return None
        return nearest_ghost.direction
    
if __name__ == "__main__":
    game = GameController()
    game.startGame()
    while True:
        game.update()
