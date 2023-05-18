# Used MacOS for this homework
import sys
import logging
from decimal import Decimal, InvalidOperation
from datetime import datetime

from bank import Bank
from accounts import OverdrawError, TransactionLimitError, TransactionSequenceError
from base import Base

import sqlalchemy
from sqlalchemy.orm.session import sessionmaker

import tkinter as tk
from tkinter.messagebox import showwarning

logging.basicConfig(filename='bank.log', level=logging.DEBUG,
                    format='%(asctime)s|%(levelname)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# error popup message
def handle_exception(exception, value, traceback):
    message = "Sorry! Something unexpected happened. If this problem persists please contact our support team for assistance."
    showwarning(
        title=exception.__name__,
        message=message
        )
    logging.error(f"{exception.__name__} : {repr(value)}")
    sys.exit(1)


class BankGUI:
    """Display a menu of options and respond to choices when run."""

    def __init__(self): 
        self._window = tk.Tk()
        self._window.title("MY BANK")

        self._session = Session()
        self._bank = self._session.query(Bank).first()
        if not self._bank:
            self._bank = Bank()
            self._session.add(self._bank)
            self._session.commit()
            logging.debug("Saved to bank.db")
        else:
            logging.debug("Loaded from bank.db")
        self._selected_account = None

        self._options_frame = tk.Frame(self._window)
        self._options_frame.grid(row=0)
        tk.Button(self._options_frame,
                text="Open Account",
                command=self._open_account).grid(row=0, column=0)
        tk.Button(self._options_frame,
                text="Add Transaction",
                command=self._add_transaction).grid(row=0, column=1)
        tk.Button(self._options_frame,
                text="Interest and Fees",
                command=self._monthly_triggers).grid(row=0, column=2)


        self._acct_frame = tk.Frame(self._window) 
        self._acct_frame.grid(row=1, column=0, ipadx=90)

        self._transactions_frame = tk.Frame(self._window)
        self._transactions_frame.grid(row=1, column=0, sticky="e")

        self._summary()

        self._window.mainloop()
        self._window.report_callback_exception = handle_exception

  
    def _open_account(self):
        def make_acct():
            acct_type = clicked.get()
            initial_deposit = deposit_entry.get()
            try:
                amt = Decimal(initial_deposit)
            except InvalidOperation: 
                message = "Please try again with a valid dollar amount."
                self._display_error("Invalid Operation", message)
            try:  
                self._bank.add_account(acct_type, amt, self._session) 
            except OverdrawError:
                message = "This transaction could not be completed due to an insufficient account balance."
                self._display_error("Overdraw Error", message)
            deposit_label.destroy()
            deposit_entry.destroy()
            acct_dropdown.destroy()
            enter_btn.destroy()
            self._summary()
            if self._selected_account:
                self._list_transactions()
            self._session.commit()
            #logging.debug("Saved to bank.db")
        
        deposit_label = tk.Label(self._options_frame, text="Initial Deposit:")
        deposit_label.grid(row=1, column=0)

        # makes amt entry only accept numbers and "." as input
        def validate_amt(input):
            if input.isdigit() or input == ".":
                return True
            else:
                return False
        check_amt = self._window.register(validate_amt)
        deposit_entry = tk.Entry(self._options_frame, validate='key',validatecommand=(check_amt,'%S'))
        deposit_entry.grid(row=2, column=0)

        acct_options =["checking", "savings"]    
        clicked = tk.StringVar()
        acct_dropdown = tk.OptionMenu(self._options_frame, clicked, *acct_options)
        acct_dropdown.grid(row=3, column=0, sticky="w")
            
        enter_btn = tk.Button(self._options_frame, text="Enter", command=make_acct)
        enter_btn.grid(row=3, column=0, sticky="e")


    def _add_transaction(self):
        def add():
            amt = amt_entry.get()
            try:
                amount = Decimal(amt)
            except InvalidOperation:
                message = "Please try again with a valid dollar amount."
                self._display_error("Invalid Operation", message)

            dt = date_entry.get()
            try:
                date = datetime.strptime(dt, "%Y-%m-%d").date()
            except ValueError:
                message = "Please try again with a valid date in the format YYYY-MM-DD."
                self._display_error("Value Error", message)

            try:
                self._selected_account.add_transaction(amount, self._session, date)
            except AttributeError:
                message = "This command requires that you first select an account."
                self._display_error("Attribute Error", message)
            except OverdrawError:
                message = "This transaction could not be completed due to an insufficient account balance."
                self._display_error("Overdraw Error", message)
            except TransactionLimitError:
                message = "This transaction could not be completed because the account has reached a transaction limit."
                self._display_error("Transaction Limit Error", message)
            except TransactionSequenceError as e:
                message = "New transactions must be from {} onward.".format(e.latest_date)
                self._display_error("Transaction Sequence Error", message)

            amt_label.destroy()
            amt_entry.destroy()
            date_label.destroy()
            date_entry.destroy()
            enter_btn.destroy()
            self._summary()
            self._list_transactions()
            self._session.commit()
            #logging.debug("Saved to bank.db")

        amt_label = tk.Label(self._options_frame, text="Amount:")
        amt_label.grid(row=1, column=1, sticky="e")

        # makes amt entry only accept numbers and "." as input
        def validate_amt(input):
            if input.isdigit() or input == "." or input == "-":
                return True
            else:
                return False
        check_amt = self._window.register(validate_amt)
        amt_entry = tk.Entry(self._options_frame, validate='key',validatecommand=(check_amt,'%S'))
        amt_entry.grid(row=1, column=2)

        date_label = tk.Label(self._options_frame, text="Date:")
        date_label.grid(row=2, column=1, sticky="e")

        # makes date entry only accept numbers and "-" as input
        def validate_date(input):
            if input.isdigit() or input == "-":
                return True
            else:
                return False
        check_date = self._window.register(validate_date)
        date_entry = tk.Entry(self._options_frame, validate='key',validatecommand=(check_date,'%S'))
        date_entry.grid(row=2, column=2)

        enter_btn = tk.Button(self._options_frame, text="Enter", command=add)
        enter_btn.grid(row=3, column=2)


    def _monthly_triggers(self):
        try:
            self._selected_account.assess_interest_and_fees(self._session)
        except AttributeError:
            message = "This command requires that you first select an account."
            self._display_error("Attribute Error", message)
        except TransactionSequenceError as e:
            message = "Cannot apply interest and fees again in the month of {}.".format(e.latest_date.strftime('%B'))
            self._display_error("Transaction Sequence Error", message)
        self._summary()
        self._list_transactions()
        self._session.commit()
        #logging.debug("Saved to bank.db")


    def _summary(self):
        # selected Radiobutton = curr selected account
        def select():
            selected_acct = self._option.get()
            self._selected_account = self._bank.get_account(selected_acct)
            self._list_transactions()

        accts = self._bank.show_accounts()    
        self._option = tk.IntVar()  
        row=1
        for x in accts:
            tk.Radiobutton(self._acct_frame, text=x, var=self._option, value=row, command=select).grid(row=row, column=0, sticky="w")
            if self._selected_account:
                self._option.set(self._selected_account._account_number)
            row+=1
        

    def _list_transactions(self):
        # clears frame
        for x in self._transactions_frame.winfo_children():
            x.destroy()
        transactions = self._selected_account.get_transactions()
        row = 1
        for t in transactions:
            value = t._amt
            if value >= 0:
                color = 'green'
            else:
                color ='red'
            tk.Label(self._transactions_frame, text=t, fg=color).grid(row=row, column=0)
            row+=1

    
    def _display_error(self, error, message):
        showwarning(
            title=error,
            message=message
        )


if __name__ == "__main__":
    engine = sqlalchemy.create_engine("sqlite:///bank.db")
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    BankGUI()