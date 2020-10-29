from __future__ import absolute_import, division, print_function
from math import sqrt, log, inf
import random
import copy
import time

# State class to represent nodes in the graph


class State:
    def __init__(self, grid, player):
        self.grid = copy.deepcopy(grid)
        self.maxrc = len(grid)-1
        self.grid_count = 11
        self.piece = player
        self.value = 0
        self.visits = 0
        self.player = player
        self.winner = None
        self.isterminal = False
        self.isfullyexpanded = False
        self.children = []
        self.move = None
        self.parent = None


class MCTS:
    def __init__(self, grid, player):
        self.grid = copy.deepcopy(grid)
        self.player = player
        self.root = State(grid, player)

    # MCTS

    def uct_search(self):
        # timer to run algorithm for 15 seconds
        starttime = time.time()
        while(time.time() - starttime <= 15):
            s = self.selection(self.root)
            winner = self.simulation(s)
            self.backpropagation(s, winner)
        return self.root_best_child(self.root).move

    # function to choose the best root choice

    def root_best_child(self, state):
        ret = None
        bestvalue = -inf
        for child in state.children:
            currvalue = (child.value/child.visits)
            if currvalue > bestvalue:
                bestvalue = currvalue
                ret = child
        return ret

    # Tree policy

    def selection(self, state):
        while state.isterminal == False:
            # check if node is fully expanded
            if (self.is_fully_expanded(state) == False):
                return self.expansion(state)
            else:
                state = self.best_child(state)
        pass

    # Check if node is fully expanded by seeing if num children is equal to options
    def is_fully_expanded(self, state):
        options = self.get_options(state.grid, state)
        if len(state.children) == len(options):
            state.isfullyexpanded = True
            return True
        else:
            return False

    # Expand

    def expansion(self, state):
        # create a copy of the current grid to make a child
        childstate = State(state.grid, state.player)
        childmove = self.make_move(childstate)
        self.set_piece(childmove[0], childmove[1], childstate)
        # attach child node to grid
        childstate.move = childmove
        state.children.append(childstate)
        childstate.parent = state
        return childstate

    # select best child when expanding

    def best_child(self, state):
        ret = None
        max = -inf
        for child in state.children:
            if child.visits == 0:
                return child
            banditvalue = (child.value/child.visits) + 2 * \
                sqrt(log(state.visits)/(child.visits))
            if banditvalue > max:
                max = banditvalue
                ret = child
        return ret

    # default policy

    def simulation(self, state):
        # make deep copy of state to run simulation on
        simulationstate = State(state.grid, state.player)
        while (simulationstate.isterminal == False):
            nextmove = self.make_move(simulationstate)
            # If no moves can be made then white is the winner
            if (nextmove == -1):
                simulationstate.winner = 'w'
                simulationstate.isterminal = True
                return simulationstate
            self.set_piece(nextmove[0], nextmove[1], simulationstate)
            self.check_win(nextmove[0], nextmove[1], simulationstate)
            if (simulationstate.isterminal == True):
                return simulationstate
        return simulationstate

    # send values back up

    def backpropagation(self, state, result):
        while state.parent != None:
            state.visits += 1
            if (state.player == result.winner):
                state.value += 1
            else:
                state.value -= 1
            state = state.parent
        self.root.visits += 1

    def get_options(self, grid, state):
        # collect all occupied spots
        current_pcs = []
        for r in range(len(grid)):
            for c in range(len(grid)):
                if not grid[r][c] == '.':
                    current_pcs.append((r, c))
        # At the beginning of the game, curernt_pcs is empty
        if not current_pcs:
            return [(state.maxrc//2, state.maxrc//2)]
        # Reasonable moves should be close to where the current pieces are
        # Think about what these calculations are doing
        # Note: min(list, key=lambda x: x[0]) picks the element with the min value on the first dimension
        min_r = max(0, min(current_pcs, key=lambda x: x[0])[0]-1)
        max_r = min(state.maxrc, max(current_pcs, key=lambda x: x[0])[0]+1)
        min_c = max(0, min(current_pcs, key=lambda x: x[1])[1]-1)
        max_c = min(state.maxrc, max(current_pcs, key=lambda x: x[1])[1]+1)
        # Options of reasonable next step moves
        options = []
        for i in range(min_r, max_r+1):
            for j in range(min_c, max_c+1):
                if not (i, j) in current_pcs:
                    options.append((i, j))
        #print("length of options is ", len(options))
        if len(options) == 0:
            # In the unlikely event that no one wins before board is filled
            # Make white win since black moved first
            state.isterminal = True
            # self.ch
        return options

    # Select a random move to make based on all possible moves
    def make_move(self, state):
        choices = self.get_options(state.grid, state)
        if (len(choices) == 0):
            return -1
        return random.choice(choices)

    # add a piece to the board

    def set_piece(self, r, c, state):
        if state.grid[r][c] == '.':
            state.grid[r][c] = state.piece
            if state.piece == 'b':
                state.piece = 'w'
            else:
                state.piece = 'b'
            return True
        return False

    # Helper function for make move
    def get_continuous_count(self, r, c, dr, dc, state):
        piece = state.grid[r][c]
        result = 0
        i = 1
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < state.grid_count and 0 <= new_c < state.grid_count:
                if state.grid[new_r][new_c] == piece:
                    result += 1
                else:
                    break
            else:
                break
            i += 1
        return result

    # check if a winning move has been made
    def check_win(self, r, c, state):
        n_count = self.get_continuous_count(r, c, -1, 0, state)
        s_count = self.get_continuous_count(r, c, 1, 0, state)
        e_count = self.get_continuous_count(r, c, 0, 1, state)
        w_count = self.get_continuous_count(r, c, 0, -1, state)
        se_count = self.get_continuous_count(r, c, 1, 1, state)
        nw_count = self.get_continuous_count(r, c, -1, -1, state)
        ne_count = self.get_continuous_count(r, c, -1, 1, state)
        sw_count = self.get_continuous_count(r, c, 1, -1, state)
        if (n_count + s_count + 1 >= 5) or (e_count + w_count + 1 >= 5) or \
                (se_count + nw_count + 1 >= 5) or (ne_count + sw_count + 1 >= 5):
            # self.winner = self.grid[r][c]
            state.winner = state.grid[r][c]
            state.isterminal = True
            # self.game_over = True
