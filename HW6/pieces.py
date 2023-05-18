DIRECTIONS = {"n": (0, 1), "ne": (1, 1), "e": (1, 0), "se": (1, -1), "s": (0, -1), "sw": (-1, -1), "w": (-1, 0), "nw": (-1, 1)}

class WorkerError(Exception):
    """Handles cases where a user enters anything other than A, B, Y, or Z 
    or selects one of the opponent's pieces"""
    def __init__(self, message):
        self.message = message

class DirectionError(Exception):
    """Handles cases where a user enters anything other than n, ne, e, se, s, sw, w, nw 
    or enters a valid direction that the worker cannot move into or build on"""
    def __init__(self, message):
        self.message = message



class Space:
    def __init__(self, x, y, letter=" "):
        self.position = (x, y)
        self.level = 0
        self.occupied = letter != " "
        self.contents = "0" + letter

        # edge space has center_score = 0
        if x == 0 or y == 0 or x == 4 or y == 4: 
            self.value = 0
        # ring space has center_score = 1
        elif x == 1 or y == 1 or x == 3 or y == 3:
            self.value = 1
        # middle space has center_score = 2
        else:
            self.value = 2



class Board:
    def __init__(self):
        self.grid = {}
        # set up grid
        worker_coordinates = [(1, 1, 'A'), (3, 3, 'B'), (1, 3, 'Y'), (3, 1, 'Z')]
        for x in range(4, -1, -1):
            for y in range(4, -1, -1):
                space = Space(x, y)
                for coordinate in worker_coordinates:
                    if (x, y) == coordinate[:2]:
                        space = Space(x, y, coordinate[2])
                        break
                self.grid[(x, y)] = space

    def print_board(self):
        for y in range(4, -1, -1):
            row = '|'.join(self.grid[(x, y)].contents for x in range(5))
            print('+--+--+--+--+--+\n' + '|' + row + '|')
        print('+--+--+--+--+--+')
              

class Worker:
    def __init__(self, letter):
        self.letter = letter
        self.color = 'white' if letter in ('A', 'B') else 'blue'
        positions = {'A': (1, 1), 'B': (3, 3), 'Y': (1, 3), 'Z': (3, 1)}
        self.position = positions.get(letter)


    def valid_moves(self, worker_pos, board, build=False):
        # returns dictionary with possible directions to move and the coordinates of the new space they would land on 
        valid_moves = {}
        for direction, (dx, dy) in DIRECTIONS.items():
            new_x, new_y = worker_pos[0] + dx, worker_pos[1] + dy
            if not (0 <= new_x <= 4 and 0 <= new_y <= 4):
                continue
            new_space = board.grid[(new_x, new_y)]
            if new_space.occupied or new_space.level == 4:
                continue
            if not build and new_space.level - board.grid[worker_pos].level > 1:
                continue
            valid_moves[direction] = (new_x, new_y)
        return valid_moves
    

    def worker_move(self, board, move_coords):
        old_position = self.position
        self.position = move_coords
        
        old_space = board.grid[old_position]
        old_space.contents = str(old_space.level) + ' '
        old_space.occupied = False

        new_space = board.grid[self.position]
        new_space.contents = str(new_space.level) + self.letter
        new_space.occupied = True


    def worker_build(self, board, build_coords):
        target_space = board.grid.get(build_coords)
        target_space.level += 1
        target_space.contents = str(target_space.level) + " "
        target_space.occupied = False
        




