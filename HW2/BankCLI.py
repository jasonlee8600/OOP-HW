import sys
import pickle
import calendar
import logging
from decimal import Decimal, InvalidOperation
from datetime import datetime
from bank import Bank
from transactions import Transaction
from accounts import OverdrawError, TransactionSequenceError, TransactionLimitError


# makes logs write to bank.log in certain format
logging.basicConfig(filename='bank.log', level=logging.DEBUG, format='%(asctime)s|%(levelname)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')


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
            try:
                action()
            except TypeError:
                print("{0} is not a valid choice.".format(choice))
            except AttributeError:
                print("This command requires that you first select an account.")
            except OverdrawError:
                print("This transaction could not be completed due to an insufficient account balance.")
            except TransactionSequenceError as error:
                latest_date = error.latest_date
                if error.monthly_trigger == False:
                    print("New transactions must be from {0} onward.".format(latest_date))
                else:
                    print("Cannot apply interest and fees again in the month of {0}.".format(calendar.month_name[latest_date.month]))
            except TransactionLimitError as error:
                limit = error.limit
                day_or_month = error.day_or_month
                print("This transaction could not be completed because this account already has {0} transactions in this {1}.".format(limit, day_or_month))
            
           

    def _summary(self):
        """Print out each account and its current balance"""
        # another connection to Account objects
        for x in self._bank.show_accounts():
            print(x)

    def _load(self):
        """Loads previously saved Bank object"""
        with open("bank.pickle", "rb") as f:
            self._bank = pickle.load(f)
        # clearing the selected account so it doesn't get out of sync with the new account objects loaded from the pickle file
        self._selected_account = None
        logging.debug("Loaded from bank.pickle")


    def _save(self):
        """Saves a single Bank object by pickling"""
        with open("bank.pickle", "wb") as f:
            pickle.dump(self._bank, f)
        logging.debug("Saved to bank.pickle")


    def _quit(self):
        """Exits the program"""
        sys.exit(0)

    def _add_transaction(self):
        """Adds a transaction to the currently selected account"""
        amount = input("Amount?\n>")
        try:
            Decimal(amount)
        except InvalidOperation:
            print("Please try again with a valid dollar amount.")
            self._add_transaction()
        else:
            self._prompt_date(amount)


    def _prompt_date(self, amount):
        """Prompts for date on transaction until valid input entered"""
        date = input("Date? (YYYY-MM-DD)\n>")
        try:
            datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            print("Please try again with a valid date in the format YYYY-MM-DD.")
            # repropmt for another date
            self._prompt_date(amount)
        else:
            t = Transaction(amount, date)
            self._selected_account.add_transaction(t)
        

    def _open_account(self, acct_type=None):
        """Creates either a new CheckingAccount or SavingsAccount and prompts for an amount for an initial deposit"""
        if acct_type is None:
            acct_type = input("Type of account? (checking/savings)\n>")
        initial_deposit = input("Initial deposit amount?\n>")
        try:
            Decimal(initial_deposit)
        except InvalidOperation:
            print("Please try again with a valid dollar amount.")
            self._open_account(acct_type)
        else:
            t = Transaction(initial_deposit)
            a = self._bank.add_account(acct_type)
            a.add_transaction(t)

    def _select(self):
        """Selects account to set as current account being accessed"""
        num = int(input("Enter account number\n>"))
        self._selected_account = self._bank.get_account(num)

    def _monthy_triggers(self):
        """Assesses interest and fees on currently selected account"""
        self._selected_account.assess_interest_and_fees()

    def _list_transactions(self):
        """Print out all the transactions of the currently selected account sorted by date"""
        for x in self._selected_account.get_transactions():
            print(x)


if __name__ == "__main__":
    try:
        BankCLI().run()
    except Exception as err:
        message = "Sorry! Something unexpected happened. If this problem persists please contact our support team for assistance."
        print(message)
        logging.error("%s: %s", type(err).__name__, repr(message))
