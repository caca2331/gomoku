# by Xincheng Shen, A15302572
from __future__ import absolute_import, division, print_function

import time
from math import sqrt, log
import random
import sys

# To the user(grader): feel free to toggle the following five constants
debugTrace = False
debugTraceChildren = False
debugStats = True
time_limit = 3  # how long MCTS will run
cp = 1  # the constant in UCT equation


# to evaluate the current state
class State:
    grid_count = None  # grid count for each side
    grid_count_1 = None  # grid count - 1
    total_grid_count = None  # total squares
    tier1_offset_1d = None  # 1d_grid's offset of all surrounding squares

    def __init__(self, grid=None, player=None, options=None):
        self.grid = grid
        self.player = player
        self.winner = None
        self.parent = None
        self.children = []
        self.options = options
        self.last_move = 0
        self.total_attempt = 0
        self.score = 0  # score of root player

    # initialize 2d grid to 1d grid, static variables
    def initialize(self, grid, player):
        State.grid_count = len(grid)
        State.grid_count_1 = State.grid_count - 1
        State.total_grid_count = State.grid_count * State.grid_count
        State.tier1_offset_1d = [-1 - State.grid_count, 0 - State.grid_count, 1 - State.grid_count, -1, 1,
                                 -1 + State.grid_count, State.grid_count, 1 + State.grid_count]
        self.grid = State.convert_2d_to_1d_grid(grid)
        self.player = player
        self.last_move = 0 - State.grid_count
        self.options = []
        self.initialize_options()

    # get all options on the board
    def initialize_options(self):
        # logic 1: get all within 1 square
        for i in range(State.total_grid_count):
            # for each occupied square
            if self.grid[i] == 'w' or self.grid[i] == 'b':
                # for the valid empty squares around it
                for offset in State.tier1_offset_1d:
                    new_index = offset + i
                    if 0 <= new_index < State.total_grid_count and self.grid[new_index] == '.':
                        col = i % State.grid_count
                        if 0 < col < State.grid_count_1 or col + new_index % State.grid_count != State.grid_count_1:
                            self.grid[new_index] = '*'
                            self.options.append(new_index)

        # Common logic: if empty board, play on the center
        if len(self.options) == 0:
            # case of empty board, play on the center
            if self.grid[0] == '.':
                self.options.append((State.grid_count // 2 * State.grid_count + State.grid_count // 2))
            else:
                # In the unlikely event that no one wins before board is filled
                # Make winner "draw"
                self.winner = 'd'

    @staticmethod
    def convert_2d_to_1d_grid(grid):
        # (0,0):a (0,1):b   ->
        # (1,0):c (1,1):d   ->   (0):a (1):b (2):c (3):d
        # (r,c) -> (r * State.grid_count + c)
        new_grid = []
        for row in grid:
            for col in row:
                new_grid.append(col)
        return new_grid

    #  move, update player, grid, win_state; return if game ends
    def move(self, d):
        # update last_move, grid
        self.grid[d] = self.player
        self.last_move = d

        # update options
        self.options.remove(d)
        for offset in State.tier1_offset_1d:
            new_index = offset + d
            if 0 <= new_index < State.total_grid_count and self.grid[new_index] == '.':
                col = d % State.grid_count
                if 0 < col < State.grid_count_1 or col + new_index % State.grid_count != State.grid_count_1:
                    self.grid[new_index] = '*'
                    self.options.append(new_index)

        # update winner and player
        self.check_will_win(d, self.player)
        self.player = 'b' if self.player == 'w' else 'w'

    # return if a player will win if he plays on certain location
    def check_will_win(self, d, player):
        # check more than continuous 5 stones
        if self.has_continuous(d, player, 5):
            self.winner = player
            return True
        # check draw
        if len(self.options) == 0:
            self.winner = 'd'
            return True

        return False

    # return total continuous_count in both positive and negative direction
    def get_continuous_count(self, d, dd, player):
        result = 1  # the center stone is 1
        temp_index = d  # the given direction
        while True:
            new_index = temp_index + dd
            if 0 <= new_index < State.total_grid_count and self.grid[new_index] == player:
                col = temp_index % State.grid_count
                if 0 < col < State.grid_count_1 or col + new_index % State.grid_count != State.grid_count_1:
                    result += 1
                    temp_index = new_index
                else:
                    break
            else:
                break
        temp_index = d  # count the other direction
        while True:
            new_index = temp_index - dd
            if 0 <= new_index < State.total_grid_count and self.grid[new_index] == player:
                col = temp_index % State.grid_count
                if 0 < col < State.grid_count_1 or col + new_index % State.grid_count != State.grid_count_1:
                    result += 1
                    temp_index = new_index
                else:
                    break
            else:
                break

        return result

    # return true if has a continuous stone of count
    def has_continuous(self, d, player, count):
        # |, -, \, /
        return self.get_continuous_count(d, State.grid_count, player) >= count or \
               self.get_continuous_count(d, 1, player) >= count or \
               self.get_continuous_count(d, State.grid_count + 1, player) >= count or \
               self.get_continuous_count(d, State.grid_count - 1, player) >= count

    # # check if the location is valid after moving a certain offset
    # @staticmethod
    # def check_in_board(original_index, d):

    # return a copy of child after certain move
    # Note that the parent must NOT be terminate state (must NOT be either player win)
    # Note that function do NOT append child into parent's children
    def get_child_by_move(self, d):
        # set parent, children, score and total_attempt properly
        child = State(list(self.grid), self.player, list(self.options))
        child.score = 0
        child.total_attempt = 0
        child.parent = self
        child.children = []
        # move
        child.move(d)
        return child


class MCTS:

    def __init__(self, grid, player):
        self.root = State()
        self.root.initialize(grid, player)
        self.grid_count = self.root.grid_count
        self.root_player = player
        self.grid = list(grid)
        self.start_time = time.time()
        self.expansion_ctr = 0
        self.best_child_ctr = 0
        self.simulation_ctr = 0
        self.expansion_timer = 0
        self.best_child_timer = 0
        self.simulation_timer = 0
        self.simulation_step_ctr = 0
        self.lv1_trim_ctr = 0
        self.lv2_trim_ctr = 0

    def make_move(self):
        move_1d = self.uct_search().last_move
        return move_1d // self.grid_count, move_1d % self.grid_count

    def uct_search(self):
        while time.time() - self.start_time < time_limit:
            if debugTrace:
                sys.stdout.write("--- root ")
            temp_node = self.tree_policy(self.root)
            reward = self.simulation(temp_node)
            self.backpropagation(temp_node, reward)
            if debugTrace:
                sys.stdout.write("\n")
                sys.stdout.flush()

        if debugStats:
            duration = time.time() - self.start_time
            print("\n*** efficiency summary ***")
            print("expansion:", self.expansion_ctr, '-', self.expansion_timer / duration * 100, "%")
            print("best_child:", self.best_child_ctr, '-', self.best_child_timer / duration * 100, "%")
            print("simulation:", self.simulation_ctr, '-', self.simulation_timer / duration * 100, "% simmed",
                  self.simulation_step_ctr, "moves")
            print("trimmed:", self.lv1_trim_ctr, self.lv2_trim_ctr)

            # for the last move, we don't need to explore any more, just output
            return self.best_child(self.root, 0)

    def tree_policy(self, state):
        # while not terminated
        while state.winner is None:

            if debugTrace:
                sys.stdout.write("(")
                sys.stdout.write(str(state.last_move // self.grid_count))
                sys.stdout.write(",")
                sys.stdout.write(str(state.last_move % self.grid_count))
                sys.stdout.write(" ")
                sys.stdout.write(str(state.score))
                sys.stdout.write("/")
                sys.stdout.write(str(state.total_attempt))
                sys.stdout.write(") has ")

            # if not fully terminated
            if len(state.options) > len(state.children):

                # expand
                return self.expansion(state)
            else:
                state = self.best_child(state, cp)

        if debugTrace:
            sys.stdout.write("(")
            sys.stdout.write(str(state.last_move // self.grid_count))
            sys.stdout.write(",")
            sys.stdout.write(str(state.last_move % self.grid_count))
            sys.stdout.write(" ")
            sys.stdout.write(str(state.score))
            sys.stdout.write("/")
            sys.stdout.write(str(state.total_attempt))
            sys.stdout.write(") has ")

        return state

    # expand an non-fully expanded state
    def expansion(self, state):

        if debugStats:
            self.expansion_ctr += 1
            self.expansion_timer -= time.time()

        # return first option that not yet have corresponding child
        child = state.get_child_by_move(state.options[len(state.children) - 1])
        state.children.append(child)

        # if expansion makes player win, make parent always choose it (cut other branches)
        state = child
        while (state is not self.root) and (state.winner is not None):
            parent = state.parent
            if state.winner == parent.player:
                parent.winner = state.winner
                # score = parent.total_attempt - parent.score if parent.winner == self.root_player else - parent.score
                # self.backpropagation(state, score)
                self.lv1_trim_ctr += 1
            else:
                skip = False
                for bro_and_sis in parent.children:
                    if bro_and_sis.winner is None:
                        skip = True
                        break
                if not skip:
                    parent.winner = state.winner
                    # score = parent.total_attempt - parent.score if parent.winner == self.root_player else - parent.score
                    # self.backpropagation(state, score)
                    self.lv2_trim_ctr += 1
            state = parent

        if debugStats:
            self.expansion_timer += time.time()
        if debugTrace:
            sys.stdout.write("expansion: (")
            sys.stdout.write(str(child.last_move // self.grid_count))
            sys.stdout.write(",")
            sys.stdout.write(str(child.last_move % self.grid_count))
            sys.stdout.write(")")

        return child

    # return best child for current player
    def best_child(self, state, c):

        if debugStats:
            self.best_child_ctr += 1
            self.best_child_timer -= time.time()

        current_max = -99999999
        max_child = None
        for i in range(len(state.children)):
            child = state.children[i]
            # q is score if current state's player is same as root player, otherwise total_attempt - score
            q = child.score if self.root_player == state.player else child.total_attempt - child.score
            # win-rate point + exploration point
            temp = q / child.total_attempt + c * sqrt(2 * log(state.total_attempt) / child.total_attempt)

            if debugTrace and debugTraceChildren:
                sys.stdout.write(str(child.last_move // self.grid_count))
                sys.stdout.write(",")
                sys.stdout.write(str(child.last_move % self.grid_count))
                sys.stdout.write(" ")
                sys.stdout.write(str(q / child.total_attempt))
                sys.stdout.write(",")
                sys.stdout.write(str(temp))
                sys.stdout.write(" |")

            if temp > current_max:
                current_max = temp
                max_child = child

        if debugStats:
            self.best_child_timer += time.time()
        if debugTrace and debugTraceChildren:
            sys.stdout.write("-->\n")

        return max_child

    def backpropagation(self, state, reward):
        while state is not None:
            state.total_attempt += 1
            state.score += reward
            state = state.parent

    def simulation(self, state):

        if debugStats:
            self.simulation_ctr += 1
            self.simulation_timer -= time.time()

        return self.simulation_strategy_1(state)

    # roll out until end of game.
    def simulation_strategy_1(self, state):
        rollout_counter = 0
        # check if no winner yet
        if state.winner is None:
            state = state.get_child_by_move(random.choice(state.options))
            # keep randomly playing until one player wins
            while state.winner is None:
                state.move(random.choice(state.options))
                rollout_counter += 1
                if rollout_counter > 15:
                    state.winner = 'd'

        if debugStats:
            self.simulation_timer += time.time()
            self.simulation_step_ctr += rollout_counter
        if debugTrace:
            sys.stdout.write(" winner: ")
            sys.stdout.write(state.winner)
            sys.stdout.write(" in ")
            sys.stdout.write(str(rollout_counter))
            sys.stdout.write(" steps")

        # reward is 1 if root player wins, 0.5 if draw, 0 otherwise
        return 1 if state.winner == self.root_player else 0.5 if state.winner == 'd' else 0

    # roll until temporary options are filled.
    def simulation_strategy_2(self, state):
        rollout_counter = 0
        # check if no winner yet
        if state.winner is None:
            for option in state.options:
                rollout_counter += 1
                if state.check_will_win(option, state.winner):
                    state.options = [option]
                    break

        if debugStats:
            self.simulation_timer += time.time()
            self.simulation_step_ctr += rollout_counter
        if debugTrace:
            # sys.stdout.write(" winner: ")
            # sys.stdout.write(state.winner)
            sys.stdout.write(" in ")
            sys.stdout.write(str(rollout_counter))
            sys.stdout.write(" steps")

        # reward is 1 if root player wins, 0.5 if draw, 0 otherwise
        return 1 if state.winner == self.root_player else 0.5 if state.winner is None else 0

    # if there exists
    def check_win_in_one_step(self, state):
        for option in state.options:
            if state.check_will_win(option, state.winner):
                state.options = [option]
                return True
        return False
