import sys
from pieces import DIRECTIONS, WorkerError, DirectionError, Board
from player import Player, HumanPlayer, RandomPlayer, HeuristicPlayer

class Game:
    def __init__(self, p1_type='human', p2_type='human', undo_redo='off', score='off'):
        self._board = Board()
        self._undo_redo = undo_redo
        self._score = score

        if p1_type == 'human':
            self._player1 = HumanPlayer('white')
        elif p1_type == 'random':
            self._player1 = RandomPlayer('white')
        else:
            self._player1 = HeuristicPlayer('white')

        if p2_type == 'human':
            self._player2 = HumanPlayer('blue')
        elif p2_type == 'random':
            self._player2 = RandomPlayer('blue')
        else:
            self._player2 = HeuristicPlayer('blue')


    def run(self, turn_count):
        while True:
            if turn_count % 2 == 0:
                player = self._player2
                opponent = self._player1
            else:
                player = self._player1
                opponent = self._player2
            
            
            self._board.print_board()

            if self._score == "on":
                move_score, values = player.move_score(player.workers[0].position, player.workers[1].position, self._board, opponent)
                print(f"Turn: {turn_count}, {player}, {values}")
            else:
                print(f"Turn: {turn_count}, {player}")

            # At the start of each turn, check if the game is over
            over, winner = self.check_game_over()
            if over:
                if winner == 'white':
                    print("white has won")
                    sys.exit(0)
                if winner == 'blue':
                    print("blue has won")
                    sys.exit(0)


            if self._undo_redo == "on":
                decision = input("undo, redo, or next\n")
                if decision != 'next':
                    break

            letter, move_dir, build_dir = player.make_move(self._board, opponent)
            
            if not isinstance(player, HumanPlayer):
                print(f"{letter},{move_dir},{build_dir}")
            
            turn_count += 1
            if self._undo_redo == "on":
                break
        return decision
        

            


    
    def check_game_over(self):
        spaces = self._board.grid
        for key in spaces.keys():
            space = spaces.get(key)
            # check if a worker is on a level 3 building
            if space.level == 3 and space.occupied:
                worker = space.contents[1]
                if worker == 'A' or worker == 'B':
                    return True, 'white'
                else:
                    return True, 'blue'
        # check if either team's workers has any valid moves left
        p1_w1 = self._player1.workers[0]
        p1_w1_valid_moves = p1_w1.valid_moves(p1_w1.position, self._board)
        p1_w2 = self._player1.workers[1]
        p1_w2_valid_moves = p1_w2.valid_moves(p1_w2.position, self._board)
        # blue wins bc neither white worker has valid moves left
        if len(p1_w1_valid_moves) == 0 and len(p1_w2_valid_moves) == 0:
            return True, 'blue'
        p2_w1 = self._player2.workers[0]
        p2_w1_valid_moves = p2_w1.valid_moves(p2_w1.position, self._board)
        p2_w2 = self._player2.workers[1]
        p2_w2_valid_moves = p2_w2.valid_moves(p2_w2.position, self._board)
        # white wins bc neither blue worker has valid moves left
        if len(p2_w1_valid_moves) == 0 and len(p2_w2_valid_moves) == 0:
            return True, 'white'
        
        return False, 'n/a'

            
