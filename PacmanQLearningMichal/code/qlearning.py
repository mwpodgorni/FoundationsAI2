from __future__ import annotations

# avoiding circular dependency
from genericpath import exists
import os
from typing import TYPE_CHECKING, Any
from enum import IntEnum
import pickle
import random

import pygame
import time

from vector import Vector2
from run import GameController
from constants import UP, DOWN, RIGHT, LEFT


class State:
    def __init__(self, playerPosition: tuple, playerDir:str,  pellets: list[tuple], powerPellets: list[tuple],
                  nearestDangerGhost: float, ghostDirection:str, scaredGhosts: list[tuple]) -> None:
        # TODO: Add more variables in the state so that the agent can account for more things in its environment
        # examples: (ghosts,)
        # warning: The more variables you add, the more space it will have search and it will take more time to train
        # print('inti state', playerPosition, pellets, powerPellets, dangerGhosts)
        self.playerPosition = playerPosition
        self.playerDir = playerDir
        self.pellets = pellets
        self.powerPellets = powerPellets
        self.nearestDangerGhost = nearestDangerGhost
        self.nearestDangerGhostDir = ghostDirection
        self.scaredGhosts = scaredGhosts

    def __str__(self) -> str:
        return "{}.{}.{}".format(self.nearestDangerGhost,self.playerDir, self.nearestDangerGhostDir) 
        # return "{}.{} | {} | {}.{}.{}".format(self.playerPosition[0], self.playerPosition[1], 
        #                                             self.nearestDangerGhost,
        #                                             len(self.pellets), len(self.powerPellets), len(self.scaredGhosts))


class Action(IntEnum):
    UP = UP
    DOWN = DOWN
    LEFT = LEFT
    RIGHT = RIGHT

    def __str__(self) -> str:
        return str(self)


def hash(state: State, action: Action) -> str:
    return "{}.{}".format(str(state), str(action))


class QValueStore:
    def __init__(self, filePath: str) -> None:
        self.filePath = filePath
        self.storage: dict[str, float] = {}
        self.load(self.filePath)

    def getQValue(self, state: State, action: Action) -> float:
        h = hash(state, action)
        value = self.storage.get(h)
        if value:
            return value
        else:
            return 0.0

    def getBestAction(self, state: State, possibleActions: list[Action]) -> Action:
        return max(possibleActions, key=lambda action: self.getQValue(state, action))

    def storeQValue(self, state: State, action: Action, value: float):
        h = hash(state, action)
        self.storage[h] = value

    def save(self):
        print("Saving: dictionary size", len(self.storage))
        fw = open(self.filePath, "wb")
        pickle.dump(self.storage, fw)
        fw.close()

    # Loads a Q-table.
    def load(self, file: str):
        if os.path.exists(file):
            fr = open(file, "rb")
            self.storage = pickle.load(fr)
            print("Loading: dictionary size", len(self.storage))
            fr.close()
        else:
            self.save()


class ReinforcementProblem:
    def __init__(self) -> None:
        self.game = GameController()
        self.game.restartGameRandom()

    def getCurrentState(self) -> State:
        # return State(self.game.pacman.position)
        return State(self.game.pacmanPosition(), self.game.pacman.direction, self.game.getPellets(), self.game.getPowerPellets(), 
                     self.game.nearestDangerGhost(), self.game.nearestDangerGhostDir(), self.game.scaredGhosts())

    # Choose a random starting state for the problem.
    def getRandomState(self) -> State:
        self.game.setPacmanInRandomPosition()
        return self.getCurrentState()

    # Get the available actions for the given state.
    def getAvailableActions(self, state: State) -> list[Action]:
        directions = self.game.pacman.validDirections()

        if self.game.pacman.direction*-1 not in directions:
            directions.append(self.game.pacman.direction*-1)
        def intDirectionToString(dir: Action) -> str:
            match dir:
                case Action.UP:
                    return "UP"
                case Action.DOWN:
                    return "DOWN"
                case Action.LEFT:
                    return "LEFT"
                case Action.RIGHT:
                    return "RIGHT"
                case _:
                    return "INV"

        # print(list(map(intDirectionToString, directions)))
        return directions

    def updateGameNTimes(self, frames: int):
        for i in range(frames):
            self.game.update()

    def updateGameForSeconds(self, seconds: float):
        durationMills: float = seconds * 1000
        currentTime = pygame.time.get_ticks()
        endTime = currentTime + durationMills
        while currentTime < endTime:
            self.game.update()
            currentTime = pygame.time.get_ticks()

    # Take the given action and state, and return
    # a pair consisting of the reward and the new state.
    def takeAction(self, state: State, action: Action) -> tuple[float, State]:
        # print('takeAction')
        previousScore = self.game.score
        self.game.pacman.learntDirection = action
        self.updateGameForSeconds(0.1)
        reward = 0
        if self.game.lastPacmanMove != 'justMove':
            print('lastPacmanMove', self.game.lastPacmanMove)
        if self.game.lastPacmanMove == 'justMove':
            self.game.lastPacmanMove = None
            reward = 0
        elif self.game.lastPacmanMove == 'hitGhost':
            self.game.lastPacmanMove = None
            reward = -40
        elif self.game.lastPacmanMove == 'atePellet':
            self.game.lastPacmanMove = None
            reward = 20
        elif self.game.lastPacmanMove == 'atePowerPellet':
            self.game.lastPacmanMove = None
            reward = 30.0 
        elif self.game.lastPacmanMove == 'ateGhost':
            self.game.lastPacmanMove = None
            reward = 40.0     
        if state.nearestDangerGhost < 6000:
            distance_difference = 6000 - state.nearestDangerGhost
            penalty = (distance_difference // 1000) * 5
            reward -= penalty
            if state.playerDir*-1==state.nearestDangerGhostDir:
                reward-=100

        # TODO: Adjust the reward function to make it learn better
        # reward = self.game.score - previousScore
        if reward != 0:
            print('state', state)
            print('reward', reward)
        newState = self.getCurrentState()
        # print('new state', newState)
        return reward, newState

    # PARAMETERS:
    # Learning Rate
    # controls how much influence the current feedback value has over the stored Q-value.

    # Discount Rate
    # how much an action’s Q-value depends on the Q-value at the state (or states) it leads to.

    #  Randomness of Exploration
    # how often the algorithm will take a random action, rather than the best action it knows so far.

    # The Length of Walk
    # number of iterations that will be carried out in a sequence of connected actions.


# Updates the store by investigating the problem.
def QLearning(
    problem: ReinforcementProblem,
    iterations,
    learningRate,
    discountRate,
    explorationRandomness,
    walkLength,
):
    # Get a starting state.
    state = problem.getRandomState()
    saveIterations = 50
    i=0
    while i < iterations:
    # for i in range(iterations):
        # print('pause', problem.game.pause.paused)
        if problem.game.pause.paused:
            # print("game is paused. Waiting..")
            time.sleep(1)          
            problem.updateGameForSeconds(0.1)
            continue  
        if i % saveIterations == 0:
            print("Saving at iteration:", i)
            store.save()
        # Pick a new state every once in a while.
        if random.uniform(0, 1) < walkLength:
            state = problem.getRandomState()

        # Get the list of available actions.
        actions = problem.getAvailableActions(state)

        # Should we use a random action this time?
        if random.uniform(0, 1) < explorationRandomness:
            action = random.choice(actions)
        # Otherwise pick the best action.
        else:
            action = store.getBestAction(state, problem.getAvailableActions(state))

        # Carry out the action and retrieve the reward and new state.
        reward, newState = problem.takeAction(state, action)

        # Get the current q from the store.
        q = store.getQValue(state, action)

        # Get the q of the best action from the new state
        maxQ = store.getQValue(
            newState,
            store.getBestAction(newState, problem.getAvailableActions(newState)),
        )

        # Perform the q learning.
        q = (1 - learningRate) * q + learningRate * (reward + discountRate * maxQ)

        # Store the new Q-value.
        store.storeQValue(state, action, q)

        # And update the state.
        state = newState
        i += 1
    print('end while loop')

if __name__ == "__main__":
    # The store for Q-values, we use this to make decisions based on
    # the learning.
    store = QValueStore("training")
    problem = ReinforcementProblem()

    QLearning(problem, 100000, 0.7, 0.75, 0, 0)
