from pacman import Pacman
import pickle

class PacmanLearning(Pacman):
    def __init__(self, node, name, exploration_rho=0.3, lr_alpha=0.2, discount_rate_gamma=0.9, walk_len_nu=0.2):
        Pacman.__init__(self, node)
        self.name = name
        self.states = []  # record all positions taken
        self.states_value = {}  # state -> value
        # Q-Learning parameters
        self.exploration_rho = exploration_rho
        self.lr_alpha = lr_alpha
        self.discount_rate_gamma = discount_rate_gamma
        self.walk_len_nu = walk_len_nu
    def getHash(self, board):
        print('getHash')
    def chooseAction(self, positions, current_board, symbol):
        print('chooseAction')
        validDirections = self.game.pacman.validDirections()
        # do so,metjg
        self.game.pacman.direction =...
    def addState(self, state):
        print('addState')
    def feedReward(self, reward):
        print('feedReward')
        for st in reversed(self.states):
            if self.states_value.get(st) is None:
                self.states_value[st] = 0
            Q = self.states_value[st]
            maxQ = self.states_value[st]
            self.states_value[st] = Q * (1 - self.lr_alpha) + self.lr_alpha * (self.discount_rate_gamma * reward + maxQ)
            reward = self.states_value[st]

    def reset(self):
        self.states = []

    # Saves Q-table, for later reuse.
    def savePolicy(self):
        fw = open('policy_' + str(self.name), 'wb')
        pickle.dump(self.states_value, fw)
        fw.close()

    # Load a trained Q-table, for demo purposes or for
    # resuming training.
    def loadPolicy(self, file):
        fr = open(file, 'rb')
        self.states_value = pickle.load(fr)
        fr.close()
