#ive taken a lot of inspiration from internet and chat gpt to finish this code in last 2 days. :') 

import random
import time
from collections import deque

class PuzzleState:
    N = 16
    SOLVED_ALL_ROWS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, N]

    def __init__(self, grid):
        self.grid = grid
        self.value = 0.0
        self.solved_rows = self.count_solved_rows()
        self.state_hash = self.create_hash()
        self.hidden_count = self.count_hidden_cells()
        self.is_terminal = (self.solved_rows == 4 or (self.solved_rows == 2 and self.hidden_count == 7) or (self.solved_rows == 1 and self.hidden_count == 11))
        self.empty_cell_idx = self.grid.index(self.N)

    def hide_cells(self, limit):
        return [0 if cell > limit and cell != self.N else cell for cell in self.grid]

    def count_solved_rows(self):
        for i in range(self.N):
            if self.grid[i] != i + 1:
                if i < 4:
                    return 0
                if i < 8:
                    return 1
                return 2
        return 4

    def count_hidden_cells(self):
        return sum(1 for cell in self.grid if cell == 0)
    
    def create_hash(self):
        if self.solved_rows == 0:
            return ','.join(map(str, self.hide_cells(4)))
        elif self.solved_rows == 1:
            return ','.join(map(str, self.hide_cells(8)))
        else:
            return ','.join(map(str, self.grid))

    def get_next_state(self, move):
        new_grid = self.grid[:]
        new_grid[self.empty_cell_idx], new_grid[move] = new_grid[move], self.N
        return PuzzleState(new_grid)

    def available_moves(self):
        row, col = divmod(self.empty_cell_idx, 4)
        moves = []

        if row > 0:  
            moves.append(4 * (row - 1) + col)
        if row < 3:  
            moves.append(4 * (row + 1) + col)
        if col > 0:  
            moves.append(4 * row + col - 1)
        if col < 3:  
            moves.append(4 * row + col + 1)

        return moves
    
    def display(self):
        for i in range(4):
            for j in range(4):
                if self.grid[4*i + j] == 16:
                    print("    ", end=' ')
                elif self.grid[4*i + j] < 10:
                    print("  "+str(self.grid[4*i + j]), end=' ')
                else:
                    print(" "+str(self.grid[4*i + j]), end=' ')
            print(" ")


class SlidingPuzzle:
    def __init__(self, gamma=0.92, theta=0.08 ):
        self.state_dict = {}
        self.policy_dict = {}
        self.gamma = gamma
        self.theta = theta

    def get_reward(self, current_state, next_state):
        if next_state.solved_rows == 4:
            return 100.0
        return (next_state.solved_rows - current_state.solved_rows)

    def generate_states(self, goal_state):
        queue = deque([goal_state])
        visited = set()

        while queue:
            state = queue.popleft()
            self.state_dict[state.state_hash] = state

            if not state.is_terminal:
                state.value = random.random()

            for move in state.available_moves():
                next_state = state.get_next_state(move)

                if next_state.state_hash not in visited:
                    self.state_dict[next_state.state_hash] = next_state
                    self.policy_dict[next_state.state_hash] = random.choice(next_state.available_moves())
                    queue.append(next_state)
                    visited.add(next_state.state_hash)

    def compute_optimal_values(self):
        while True:
            delta = 0
            for _, state in self.state_dict.items():
                if state.is_terminal:
                    continue
                old_value = state.value
                move_values = []
                for move in state.available_moves():
                    if state.solved_rows <= state.get_next_state(move).solved_rows:
                        next_state = state.get_next_state(move)
                        move_value = (
                            self.get_reward(state, next_state) +
                            self.gamma * self.state_dict[next_state.state_hash].value
                        )
                        move_values.append(move_value)

                state.value = max(move_values)
                delta = max(delta, abs(old_value - state.value))
            if delta < self.theta:
                break

    def compute_optimal_policy(self):
        for state_hash, state in self.state_dict.items():
            if state.is_terminal:
                continue
            move_values = {}
            for move in state.available_moves():
                if state.solved_rows <= state.get_next_state(move).solved_rows:
                    move_values[move] = self.get_reward(state, state.get_next_state(move)) + self.gamma * self.state_dict[state.get_next_state(move).state_hash].value
            best_move = max(move_values, key=move_values.get)
            self.policy_dict[state_hash] = best_move

    def play_and_display(self, initial_state):
        current_state = initial_state
        print("Initial State:")
        current_state.display()
        print("\n\n")
        t = 0
        time.sleep(0.1)
        while current_state.solved_rows != 4:
            move = self.policy_dict.get(current_state.state_hash)
            if move is not None:
                next_state = current_state.get_next_state(move)
            else:
                next_state = current_state.get_next_state(random.choice(current_state.available_moves()))
            current_state = next_state
            current_state.display()
            t += 1
            print(" ")
            time.sleep(0.2)
        print('Total number of steps :', t )

    def generate_random_puzzle(self, num_moves=10000):
        grid = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        for _ in range(num_moves):
            available_moves = PuzzleState(grid).available_moves()
            random_move = random.choice(available_moves)
            grid = PuzzleState(grid).get_next_state(random_move).grid
        return PuzzleState(grid)
    
    def execute(self):
        self.generate_states(PuzzleState(PuzzleState.SOLVED_ALL_ROWS))
        self.compute_optimal_values()
        self.compute_optimal_policy()
        random_puzzle = self.generate_random_puzzle()
        self.play_and_display(random_puzzle)

# Run the puzzle solution
puzzle_game = SlidingPuzzle()
puzzle_game.execute()
