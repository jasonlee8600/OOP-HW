import random
import sys
from pieces import DIRECTIONS, WorkerError, DirectionError, Board, Worker

class Player:
    def __init__(self, color):
        self.color = color
        self.workers = [Worker('A' if color == 'white' else 'Y'),
                        Worker('B' if color == 'white' else 'Z')]

    def __str__(self) -> str:
        return f"{self.color} ({self.workers[0].letter}{self.workers[1].letter})"
    
    def make_move(self, board, opponent=None):
        pass

    def random_build(self, board, worker):
        valid_builds = worker.valid_moves(worker.position, board, True)
        build_dir, build_coords = random.choice(list(valid_builds.items()))

        worker.worker_build(board, build_coords)
        return build_dir

    def move_score(self, wkr1_pos, wkr2_pos, board, opponent):
        space1, space2 = board.grid.get(wkr1_pos), board.grid.get(wkr2_pos)
        height_score = space1.level + space2.level
        center_score = space1.value + space2.value

        opp1_pos = opponent.workers[0].position
        opp2_pos = opponent.workers[1].position

        dist_wkr1_opp1 = max(abs(wkr1_pos[0] - opp1_pos[0]), abs(wkr1_pos[1] - opp1_pos[1]))
        dist_wkr2_opp1 = max(abs(wkr2_pos[0] - opp1_pos[0]), abs(wkr2_pos[1] - opp1_pos[1]))

        dist_wkr1_opp2 = max(abs(wkr1_pos[0] - opp2_pos[0]), abs(wkr1_pos[1] - opp2_pos[1]))
        dist_wkr2_opp2 = max(abs(wkr2_pos[0] - opp2_pos[0]), abs(wkr2_pos[1] - opp2_pos[1]))

        distance_score = 8 - (min(dist_wkr1_opp1, dist_wkr2_opp1) + min(dist_wkr1_opp2, dist_wkr2_opp2))

        move_score = (3 * height_score) + (2 * center_score) + (1 * distance_score)
        # if possible move goes to a level 3 space, 
        # make move_score large to ensure this option is chosen
        if space1.level == 3 or space2.level == 3:
            move_score = 9999999

        return move_score, (height_score, center_score, distance_score)
    

class HumanPlayer(Player):
    def __init__(self, color):
        super().__init__(color)

    def make_move(self, board, opponent=None):
        worker = None
        while not worker:
            try: 
                letter = input("Select a worker to move\n")
                if letter not in ['A', 'B', 'Y', 'Z']:
                    raise WorkerError("Not a valid worker")
                elif letter not in [w.letter for w in self.workers]:
                    raise WorkerError("That is not your worker")
                worker = self.workers[0] if self.workers[0].letter == letter else self.workers[1]
            except WorkerError as e:
                print(e.message)

        
        move_coords = None
        move_dir = None
        while not move_coords:
            try:
                dir_input = input("Select a direction to move (n, ne, e, se, s, sw, w, nw)\n") 
                valid_moves = worker.valid_moves(worker.position, board)
                if dir_input not in DIRECTIONS.keys():
                    raise DirectionError("Not a valid direction")
                elif dir_input not in valid_moves.keys():
                    raise DirectionError(f"Cannot move {dir_input}")
                move_coords = valid_moves[dir_input]
                move_dir = dir_input
            except DirectionError as e:
                print(e.message)

        worker.worker_move(board, move_coords)

        build_coords = None
        build_dir = None
        while not build_coords:
            try:
                dir_input = input("Select a direction to build (n, ne, e, se, s, sw, w, nw)\n")
                valid_moves = worker.valid_moves(worker.position, board, True)
                if dir_input not in DIRECTIONS.keys():
                    raise DirectionError("Not a valid direction")
                elif dir_input not in valid_moves.keys():
                    raise DirectionError(f"Cannot build {dir_input}")
                build_coords = valid_moves[dir_input]
                build_dir = dir_input
            except DirectionError as e:
                print(e.message)

        worker.worker_build(board, build_coords)
        return worker.letter, move_dir, build_dir        

    
class RandomPlayer(Player):
    def __init__(self, color):
        super().__init__(color)

    def make_move(self, board, opponent=None):
        worker = random.choice(self.workers)
        valid_moves = worker.valid_moves(worker.position, board)

        # if no valid moves for one worker, switch to other worker
        if len(valid_moves) == 0:
            worker = self.workers[0] if worker == self.workers[1] else self.workers[1]
            valid_moves = worker.valid_moves(worker.position, board)

        move_dir, move_coords = random.choice(list(valid_moves.items()))
        worker.worker_move(board, move_coords)
        build_dir = super().random_build(board, worker)

        return worker.letter, move_dir, build_dir


class HeuristicPlayer(Player):
    def __init__(self, color):
        super().__init__(color)
    
    def make_move(self, board, opponent=None):
        worker, best_moves = self.best_move(board, opponent)
        move_dir, move_coords = random.choice(list(best_moves.items()))
        worker.worker_move(board, move_coords)
        build_dir = super().random_build(board, worker)
        return worker.letter, move_dir, build_dir
        

    def best_move(self, board, opponent):
        worker1, worker2 = self.workers[0], self.workers[1]
        worker1_moves = worker1.valid_moves(worker1.position, board)
        worker2_moves = worker2.valid_moves(worker2.position, board)

        worker1_move_score = 0
        worker1_best_moves = {}

        worker2_move_score = 0
        worker2_best_moves = {}

        for direction, (dx, dy) in worker1_moves.items(): 
            move_score, values = self.move_score((dx, dy), worker2.position, board, opponent) 
            # if this move_score > current,
                # clear possible new coords and append
            if move_score > worker1_move_score:
                worker1_move_score = move_score
                worker1_best_moves.clear()
                worker1_best_moves[direction] = (dx, dy)
            # if equal move_score, append so can choose random option later
            if move_score == worker1_move_score:
                worker1_best_moves[direction] = (dx, dy)

        for direction, (dx, dy) in worker2_moves.items():  
            move_score, values = self.move_score((dx, dy), worker1.position, board, opponent) 
            if move_score > worker2_move_score:
                worker2_move_score = move_score
                worker2_best_moves.clear()
                worker2_best_moves[direction] = (dx, dy) 
            if move_score == worker2_move_score:
                worker2_best_moves[direction] = (dx, dy)

        if worker1_move_score > worker2_move_score:
            return worker1, worker1_best_moves
        else:
            return worker2, worker2_best_moves