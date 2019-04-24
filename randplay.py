from __future__ import absolute_import, division, print_function
import random


class Randplay:
    def __init__(self, grid, player):
        self.grid = grid
        self.maxrc = len(grid) - 1
        self.piece = player
        self.grid_size = 52
        self.grid_count = 11
        self.game_over = False
        self.winner = None

    def get_options(self, grid):
        # collect all occupied spots
        current_pcs = []
        for r in range(len(grid)):
            for c in range(len(grid)):
                if not grid[r][c] == '.':
                    current_pcs.append((r, c))
        # At the beginning of the game, curernt_pcs is empty
        if not current_pcs:
            return [(self.maxrc // 2, self.maxrc // 2)]
        # Reasonable moves should be close to where the current pieces are
        # Think about what these calculations are doing
        # Note: min(list, key=lambda x: x[0]) picks the element with the min value on the first dimension
        min_r = max(0, min(current_pcs, key=lambda x: x[0])[0] - 1)
        max_r = min(self.maxrc, max(current_pcs, key=lambda x: x[0])[0] + 1)
        min_c = max(0, min(current_pcs, key=lambda x: x[1])[1] - 1)
        max_c = min(self.maxrc, max(current_pcs, key=lambda x: x[1])[1] + 1)
        # Options of reasonable next step moves
        options = []
        for i in range(min_r, max_r + 1):
            for j in range(min_c, max_c + 1):
                if not (i, j) in current_pcs:
                    options.append((i, j))
        if len(options) == 0:
            # In the unlikely event that no one wins before board is filled
            # Make white win since black moved first
            self.game_over = True
            self.winner = 'w'
        return options

    def make_move(self):
        return random.choice(self.get_options(self.grid))

    def check_win(self, r, c):
        n_count = self.get_continuous_count(r, c, -1, 0)
        s_count = self.get_continuous_count(r, c, 1, 0)
        e_count = self.get_continuous_count(r, c, 0, 1)
        w_count = self.get_continuous_count(r, c, 0, -1)
        se_count = self.get_continuous_count(r, c, 1, 1)
        nw_count = self.get_continuous_count(r, c, -1, -1)
        ne_count = self.get_continuous_count(r, c, -1, 1)
        sw_count = self.get_continuous_count(r, c, 1, -1)
        if (n_count + s_count + 1 >= 5) or (e_count + w_count + 1 >= 5) or \
                (se_count + nw_count + 1 >= 5) or (ne_count + sw_count + 1 >= 5):
            self.winner = self.grid[r][c]
            self.game_over = True

    def set_piece(self, r, c):
        if self.grid[r][c] == '.':
            self.grid[r][c] = self.piece
            if self.piece == 'b':
                self.piece = 'w'
            else:
                self.piece = 'b'
            return True
        return False

    def get_continuous_count(self, r, c, dr, dc):
        piece = self.grid[r][c]
        result = 0
        i = 1
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
                if self.grid[new_r][new_c] == piece:
                    result += 1
                else:
                    break
            else:
                break
            i += 1
        return result

    # Roll out for default policy
    # 'b' player wins, update 'w' player reward value along the path: {'b':0, 'w':1}
    # 'w' player store, update 'b' player reward value along the path: {'b':1, 'w':0}
    def rollout(self):
        simReward = {}
        while not self.game_over:
            r, c = self.make_move()
            self.set_piece(r, c)
            self.check_win(r, c)
        # assign rewards
        if self.winner == 'b':
            simReward['b'] = 0
            simReward['w'] = 1
        elif self.winner == 'w':
            simReward['b'] = 1
            simReward['w'] = 0
        # print("Rolling out, winner is ", self.winner)
        return simReward
