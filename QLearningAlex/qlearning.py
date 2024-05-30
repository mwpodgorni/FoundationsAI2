from __future__ import annotations

# avoiding circular dependency
from genericpath import exists
import os
import time
from typing import TYPE_CHECKING, Any
from enum import IntEnum
import pickle
import random

import pygame

from vector import Vector2
from run import GameController
from constants import UP, DOWN, RIGHT, LEFT


class State:
    def __init__(self, 
                pelletDirection: int, 
                up: bool,
                down: bool, 
                left: bool, 
                right: bool
                ) -> None:
        
        self.pelletDirection = pelletDirection
        self.ghostUp = up
        self.ghostDown = down
        self.ghostLeft = left
        self.ghostRight = right
    
    def directionToString(self, dir: int) -> str:
        if dir == UP:
            return "UP"
        if dir == DOWN:
            return "DOWN"
        if dir == LEFT:
            return "LEFT"
        if dir == RIGHT:
            return "RIGHT"

    def __str__(self) -> str:
        return "Pellet : " + self.directionToString(self.pelletDirection) + " , " + "GHOST : " + str(self.ghostUp) + " , " + str(self.ghostDown) + " , " + str(self.ghostLeft) + " , " + str(self.ghostRight)

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
        return State(self.game.getPelletDirection(),
                     self.game.checkGhostInNodes(UP),
                     self.game.checkGhostInNodes(DOWN),
                     self.game.checkGhostInNodes(LEFT),
                     self.game.checkGhostInNodes(RIGHT)
                     )

    # Choose a random starting state for the problem.
    def getRandomState(self) -> State:
        self.game.setPacman
        return self.getCurrentState()

    # Get the available actions for the given state.
    def getAvailableActions(self, state: State) -> list[Action]:
        directions = self.game.pacman.validDirections()
        
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

        print(list(map(intDirectionToString, directions)))
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

    def ActionToString(self, dir: int) -> str:
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

    # Take the given action and state, and return
    # a pair consisting of the reward and the new state.
    def takeAction(self, state: State, action: Action) -> tuple[float, State]:
        
        self.game.pacman.learntDirection = action
        prevScore = self.game.score

        # print(state)
        # print("Action : " + self.ActionToString(action))

        self.updateGameForSeconds(0.1)
        
        # Initial reward
        reward = 0

        # Rewarded for going towards nearest pellet
        if action == state.pelletDirection:
            reward += 3
        else:
            # Punished for not doing so
            reward -= 1

        # Bigger rewards for increasing the score
        if prevScore < self.game.score:
            reward += 6

        # Punished for going towards a direction that contains ghosts.
        if action == LEFT and state.ghostLeft :
            reward = -20
        elif action == RIGHT and state.ghostRight :
            reward = -20
        elif action == UP and state.ghostUp :
            reward = -20
        elif action == DOWN and state.ghostDown :
            reward = -20

        newState = self.getCurrentState()
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
    state = problem.getCurrentState()
    saveIterations = 50
    # Repeat a number of times.
    i = 0
    while i < iterations:
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
        # store.storeQValue(state, action, q)

        # And update the state.
        state = newState
        i += 1


if __name__ == "__main__":
    # The store for Q-values, we use this to make decisions based on
    # the learning.
    store = QValueStore("training")
    problem = ReinforcementProblem()

    QLearning(problem, 100000, 0.7, 0.75, -1, -1)
