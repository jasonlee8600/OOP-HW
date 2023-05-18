from abc import ABC, abstractmethod
from game import Game
from copy import deepcopy


class Memento(ABC):
    @abstractmethod
    def __init__(self):
        pass


class ConcreteMemento(Memento):
    def __init__(self, state: Game, turn):
        self._state = state
        self._turn = turn
        self._board = state._board

    def get_state(self):
        return self._state

    

class Originator:
    def __init__(self, state: Game):
        self._state = state
        self.turn = 1
        self._og_state = deepcopy(state)

    def print(self):
        self._state._board.print_board()

    def decision(self):
        decision = self._state.run(self.turn)
        return decision
    
    def save(self) -> Memento:
        if self.turn == 1:
            old_state = self._og_state
            return ConcreteMemento(old_state, 1)
        else:
            old_state = deepcopy(self._state)
        return ConcreteMemento(old_state, self.turn)
    


class Caretaker:
    def __init__(self, originator: Originator) -> None:
        self._undos = {}
        self._originator = originator
        self.redos = {}
        self._undos[1] = self._originator.save()

    def backup(self) -> None:
        # backup current state in undos
        self._undos[self._originator.turn] = self._originator.save()

    def undo(self):
        if not len(self._undos):
            return
        if self._originator.turn == 1:
            self.redos[1] = self._originator._state
            self._originator._state = self._originator._og_state
        else:
            # put current game state in redo dict
            current_state = self._originator._state
            self.redos[self._originator.turn] = current_state
            # get previous turn state
            previous_state = self._undos.pop(self._originator.turn - 1)
            # make current state the prev one
            self._originator._state = previous_state.get_state()
            # decrement turn count
            self._originator.turn -= 1
            

    def redo(self):
        # do nothing if most recent turn
        if len(self.redos) != 0:
            # put current game state in undo dict
            current_state = self._originator._state
            self._undos[self._originator.turn] = current_state
            # get future state
            redo_state = self.redos.pop(self._originator.turn + 1)
            # set as current state
            self._originator._state = redo_state
            # increment turn count
            self._originator.turn += 1



