import sys
import pickle
from notebook import Notebook


class Menu:
    """Display a menu and respond to choices when run."""

    def __init__(self):
        self._notebook = Notebook()
        self._choices = {
            "1": self._show_notes,
            "2": self._search_notes,
            "3": self._add_note,
            "4": self._modify_note,
            "5": self._save,
            "6": self._load,
            "7": self._quit,
        }
        
    def _display_menu(self):
        print(
"""
Notebook Menu

1. Show all Notes
2. Search Notes
3. Add Note
4. Modify Note
5. Save
6. Load
7. Quit
""")

    def run(self):
        """Display the menu and respond to choices."""
        while True:
            self._display_menu()
            choice = input("Enter an option: ")
            action = self._choices.get(choice)
            if action:
                action()
            else:
                print("{0} is not a valid choice".format(choice))

    def _show_notes(self, notes=None):
        if notes is None:
            notes = self._notebook.all_notes()
        for note in notes:
            print(str(note))

    def _search_notes(self):
        filter_string = input("Search for: ")
        notes = self._notebook.search(filter_string)
        self._show_notes(notes)

    def _add_note(self):
        memo = input("Enter a memo: ")
        n = self._notebook.new_note(memo)
        print(n)
        print("Your note has been added.")

    def _modify_note(self):
        id = input("Enter a note id: ")
        memo = input("Enter a memo: ")
        tags = input("Enter tags: ")
        if memo:
            self._notebook.modify_memo(id, memo)
        if tags:
            self._notebook.modify_tags(id, tags)

    def _save(self):
        with open("notebook_save.pickle", "wb") as f:
            pickle.dump(self._notebook, f)

    def _load(self):
        with open("notebook_save.pickle", "rb") as f:   
            self._notebook = pickle.load(f)

    def _quit(self):
        sys.exit(0)


if __name__ == "__main__":
    Menu().run()