import sys
import pickle

from bank import Bank
from transactions import Transaction


class BankCLI():
    """Driver class for a command-line REPL interface to the Bank application"""

    def __init__(self):
        self._bank = Bank()

        # establishes relationship to Accounts
        self._selected_account = None

        self._choices = {
            "1": self._open_account,
            "2": self._summary,
            "3": self._select,
            "4": self._list_transactions,
            "5": self._add_transaction,
            "6": self._monthy_triggers,
            "7": self._save,
            "8": self._load,
            "9": self._quit,
        }

    def _display_menu(self):
        print(f"""--------------------------------
Currently selected account: {self._selected_account}
Enter command
1: open account
2: summary
3: select account
4: list transactions
5: add transaction
6: interest and fees
7: save
8: load
9: quit""")

    def run(self):
        """Display the menu and respond to choices."""

        while True:
            self._display_menu()
            choice = input(">")
            action = self._choices.get(choice)
            # expecting a digit 1-9
            if action:
                action()
            else:
                # not officially part of spec since we don't give invalid options
                print("{0} is not a valid choice".format(choice))

    def _summary(self):
        # another connection to Account objects
        for x in self._bank.show_accounts():
            print(x)

    def _load(self):

        with open("save.pickle", "rb") as f:
            self._bank = pickle.load(f)
        # clearing the selected account so it doesn't get out of sync with the new account objects loaded from the pickle file
        self._selected_account = None

    def _save(self):

        with open("save.pickle", "wb") as f:
            pickle.dump(self._bank, f)

    def _quit(self):
        sys.exit(0)

    def _add_transaction(self):
        amount = input("Amount?\n>")
        date = input("Date? (YYYY-MM-DD)\n>")

        # establishes dependency relationship to transactions
        t = Transaction(amount, date)

        self._selected_account.add_transaction(t)

    def _open_account(self):
        acct_type = input("Type of account? (checking/savings)\n>")
        initial_deposit = input("Initial deposit amount?\n>")

        t = Transaction(initial_deposit)

        a = self._bank.add_account(acct_type)
        a.add_transaction(t)

    def _select(self):
        num = int(input("Enter account number\n>"))
        self._selected_account = self._bank.get_account(num)

    def _monthy_triggers(self):
        self._selected_account.assess_interest_and_fees()

    def _list_transactions(self):
        for x in self._selected_account.get_transactions():
            print(x)


if __name__ == "__main__":
    BankCLI().run()
