import sys
from game import Game
from memento import Originator, Caretaker

def memento_game(originator, caretaker):
    while True:
        decision = originator.decision()
        if decision == "next":
            caretaker.redos.clear()
            originator.turn += 1
            caretaker.backup()
        elif decision == "undo":
            caretaker.undo()
        elif decision == "redo":
            caretaker.redo()



if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) > 2 and args[2] == 'on':
        # enable undo/redo
        originator = Originator(Game(*args))
        caretaker = Caretaker(originator)
        caretaker.backup()
        memento_game(originator, caretaker)
    else:
        game = Game(*args)
        game.run(1)

