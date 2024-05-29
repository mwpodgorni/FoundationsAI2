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
from constants import *


class State:
    def __init__(self, playerPosition, leftSafe, rightSafe, upSafe, downSafe, pelletDirection) -> None:
        self.playerPosition = playerPosition
        self.leftSafe = leftSafe
        self.rightSafe =  rightSafe
        self.upSafe = upSafe
        self.downSafe = downSafe
        self.pelletDirection = pelletDirection

    def __str__(self) -> str:
        return "Pacmn x/y: {}/{} | L:{} | R:{} | U:{} | D:{} | DIR: {}".format(self.playerPosition[0], self.playerPosition[1], self.leftSafe, self.rightSafe, self.upSafe, self.downSafe, self.pelletDirection)


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
        self.game.startGame()

    def getCurrentState(self) -> State:
        return State(self.game.pacmanPosition(), self.game.leftSafe(),
                     self.game.rightSafe(), self.game.upSafe(),
                     self.game.downSafe(), self.game.getPelletDirection())

    # Choose a random starting state for the problem.
    def getRandomState(self) -> State:
        self.game.setPacmanInRandomPosition()
        return self.getCurrentState()
    def getInitialState(self) -> State:
        return self.getCurrentState()

    # Get the available actions for the given state.
    def getAvailableActions(self, state: State) -> list[Action]:
        directions = self.game.pacman.validDirections()
        if self.game.pacman.direction == LEFT and not state.leftSafe:
            directions.append(self.game.pacman.direction*-1)
        elif self.game.pacman.direction == RIGHT and not state.rightSafe:
            directions.append(self.game.pacman.direction*-1)
        elif self.game.pacman.direction == UP and not state.upSafe:
            directions.append(self.game.pacman.direction*-1)
        elif self.game.pacman.direction == DOWN and not state.downSafe:
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
        return directions
    
    def getAvailableTargetActions(self, state: State) -> list[Action]:
        directions = self.game.pacman.validTargetDirections()
        if self.game.pacman.direction == LEFT and not state.leftSafe:
            directions.append(self.game.pacman.direction*-1)
        elif self.game.pacman.direction == RIGHT and not state.rightSafe:
            directions.append(self.game.pacman.direction*-1)
        elif self.game.pacman.direction == UP and not state.upSafe:
            directions.append(self.game.pacman.direction*-1)
        elif self.game.pacman.direction == DOWN and not state.downSafe:
            directions.append(self.game.pacman.direction*-1)
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

    def takeAction(self, state: State, action: Action) -> tuple[float, State]:
        self.game.pacman.learntDirection = action
        problem.updateGameNTimes(1)
        previousPelletCount = self.game.pellets.pelletList.__len__()
        pelletCount = self.game.pellets.pelletList.__len__()

        reward = 0
        if pelletCount<previousPelletCount:
            reward += 5
        if action == state.pelletDirection:
            reward +=10

        print('state:', state)
  
        if action == LEFT and state.leftSafe == False:
            reward -=  20  
        elif action == RIGHT and state.rightSafe == False:
            reward -= 20
        elif action == UP and state.upSafe == False:
            reward -= 20 
        elif action == DOWN and state.downSafe == False:
            reward -= 20
        newState = self.getCurrentState()
        return reward, newState
    
    def willOvershootNext(self):
        return self.game.pacman.willOvershootTarget()

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
    state = problem.getInitialState()
    saveIterations = 50
    # Repeat a number of times.
    i = 0
    while i < iterations:
        print('--------------------', i)
        if problem.game.pause.paused:
            print("game is paused. Waiting..")
            time.sleep(1)
            problem.updateGameNTimes(1)
            continue
        if i % saveIterations == 0:
            print("Saving at iteration:", i)
            store.save()
        # # Pick a new state every once in a while.
        # if random.uniform(0, 1) < walkLength:
        #     state = problem.getRandomState()

        # Get the list of available actions.
        actions = problem.getAvailableActions(state)
        if problem.willOvershootNext() is True:
            actions = problem.getAvailableTargetActions(state)


        # Should we use a random action this time?
        if random.uniform(0, 1) < explorationRandomness:
            action = random.choice(actions)
        # Otherwise pick the best action.
        else:
            action = store.getBestAction(state, actions)

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


if __name__ == "__main__":
    # The store for Q-values, we use this to make decisions based on
    # the learning.
    store = QValueStore("training")
    problem = ReinforcementProblem()

    QLearning(problem, 1000000, 0.7, 0.75, 0.4, 0)
