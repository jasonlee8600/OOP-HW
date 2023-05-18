import sys
import pickle
from decimal import Decimal
from datetime import datetime
from bank import Bank
from account import Transaction


class BankCLI:
    """Display a menu and respond to choices when run."""
    def __init__(self):
        self._bank = Bank()
        self._curr_account = None
        self._choices = {
            "1": self._open_account,
            "2": self._summary,
            "3": self._select_account,
            "4": self._list_transactions,
            "5": self._add_transaction,
            "6": self._interest_and_fees,
            "7": self._save,
            "8": self._load,
            "9": self._quit,
        }
        
    def _display_menu(self):
        print(f"""--------------------------------
Currently selected account: {self._curr_account}
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
        """Display the menu and respond to the choices"""
        while True:
            self._display_menu()
            choice = input(">")
            action = self._choices.get(choice)
            if action:
                action()
            else:
                print("{0} is not a valid choice".format(choice))


    def _open_account(self):
        """Creates either a new CheckingAccount or SavingsAccount and prompts for an amount for an initial deposit"""
        account_type = input("Type of account? (checking/savings)\n>")
        init_deposit = input("Initial deposit amount?\n>")

        # initial deposit counts as transaction on current date
        transaction = Transaction(init_deposit)

        account = self._bank.new_account(account_type)
        account.add_transaction(transaction)


    def _summary(self):
        """Print out each account and its current balance"""
        for account in self._bank._accounts:
            print(account)


    def _select_account(self):
        """Selects account to set as current account being accessed"""
        account_number = int(input("Enter account number\n>"))
        self._curr_account = self._bank.select_account(account_number)
    

    def _list_transactions(self):
        """Print out all the transactions of the currently selected account sorted by date"""
        for transaction in sorted(self._curr_account._transactions):
            print(transaction)


    def _add_transaction(self):
        """Adds a transaction to the currently selected account"""
        amount = input("Amount?\n>")
        date = input("Date? (YYYY-MM-DD)\n>")

        # only add transaction if won't cause negative balance
        if (self._curr_account.calc_balance() + Decimal(amount) >= 0):
            transaction = Transaction(amount, date)
            self._curr_account.add_transaction(transaction)


    def _interest_and_fees(self):
        """Assesses interest and fees on currently selected account"""
        self._curr_account.interest()
        self._curr_account.fees()


    def _save(self):
        """Saves a single Bank object by pickling"""
        with open("save.pickle", "wb") as f:
            pickle.dump(self._bank, f)


    def _load(self):
        """Loads previously saved Bank object"""
        with open("save.pickle", "rb") as f:   
            self._bank = pickle.load(f)


    def _quit(self):
        """Exits the program"""
        sys.exit(0)


if __name__ == "__main__":
    BankCLI().run()