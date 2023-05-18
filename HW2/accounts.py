from transactions import Transaction
from decimal import Decimal
import calendar
import logging


class OverdrawError(Exception):
    """Handles cases where a negative transaction would exceed the account balance (except for interest/fees)."""
    
class TransactionSequenceError(Exception):
    """Enforces that transactions should be made in chronological order."""
    def __init__(self, latest_transaction, monthly_trigger=False):
        self.latest_date = latest_transaction._date
        self.monthly_trigger = monthly_trigger

class TransactionLimitError(Exception):
    """Handles transactions that would exceed the daily/monthly limits"""
    def __init__(self, limit, day_or_month):
        self.limit = limit
        self.day_or_month = day_or_month
    

class Account:
    """This is an abstract class for accounts.  Provides default functionality for adding transactions, getting balances, and assessing interest and fees.  
    Accounts should be instantiated as SavingsAccounts or CheckingAccounts
    """

    def __init__(self, acct_num):
        self._transactions = []
        self._account_number = acct_num

    def _get_acct_num(self):
        """Returns selected account's number"""
        return self._account_number

    account_number = property(_get_acct_num)

    def add_transaction(self, t):
        """Checks a pending transaction to see if it is allowed and adds it to the account if it is.

        Args:
            t (Transaction): incoming transaction
        """

        # Logic is broken up into pieces and factored out into other methods.
        # This makes it easier to override specific parts of add_transaction.
        # This is called a Template Method design pattern
        balance_ok = self._check_balance(t)
        if not t.is_exempt():
            limits_ok = self._check_limits(t)
        in_order = self._check_order(t)
        first_monthly_trigger = self._first_monthly_trigger(t)

        
        if t.is_exempt():
            if not first_monthly_trigger:
                raise TransactionSequenceError(self._find_latest_trans(), True)
            else:
                self._transactions.append(t)
                logging.debug(f"Created transaction: {self._account_number}, {t._amt}")
                logging.debug("Triggered fees and interest")
        elif (balance_ok and limits_ok and in_order):
            self._transactions.append(t)
            logging.debug(f"Created transaction: {self._account_number}, {t._amt}")
        # raise error if overdrawn balance
        elif not balance_ok:
            raise OverdrawError
        # raise error if older than latest transaction
        elif not in_order:
                raise TransactionSequenceError(self._find_latest_trans())

    def _find_latest_trans(self):
        """Finds the latest transaction in an account"""
        if not self._transactions:
            return None
        else:
            sorted_trans = sorted(self._transactions)
            return sorted_trans[len(sorted_trans)-1]

    def _check_order(self, transaction):
        """Checks if pending transaction is onward from latest transaction in account"""
        # return true if no transactions (ex: opening account)
        if not self._transactions:
            return True
        else:
            latest_transaction = self._find_latest_trans()
            return latest_transaction <= transaction


    def _check_balance(self, t):
        """Checks whether an incoming transaction would overdraw the account

        Args:
            t (Transaction): pending transaction

        Returns:
            bool: false if account is overdrawn
        """
        return t.check_balance(self.get_balance())

    def _check_limits(self, t):
        """Parent function to check transaction limits"""
        return True

    def get_balance(self):
        """Gets the balance for an account by summing its transactions

        Returns:
            Decimal: current balance
        """
        # could have a balance variable updated when transactions are added (or removed) which is faster
        # but this is more foolproof since it's always in sync with transactions
        # this could be improved by caching the sum to avoid too much
        # recalculation, while still maintaining the list as the ground truth
        return sum(x for x in self._transactions)

    def _interest(self):
        """Calculates interest for an account balance and adds it as a new transaction exempt from limits.
        """
        end_month = self._end_of_month()
        t = Transaction(self.get_balance() * self._interest_rate, str(end_month), exempt=True)
        self.add_transaction(t)

    def _end_of_month(self):
        """Sets date for interest/fees transaction to end of month of latest transaction"""
        latest_trans = self._find_latest_trans()
        latest_date = latest_trans._date
        latest_date = latest_date.replace(day = calendar.monthrange(latest_date.year, latest_date.month)[1])
        return latest_date

    def _fees(self):
        """Parent function to assess fees"""
        pass

    def _first_monthly_trigger(self, transaction):
        """Checks if pending interest/fees is the only monthly trigger in latest transaction's month"""
        latest_trans = self._find_latest_trans()
        if latest_trans is None:
            return True
        if transaction.in_same_month(latest_trans) and latest_trans._exempt == True:
            return False
        return True

    def assess_interest_and_fees(self):
        "Trigger interest and fees calculation for this account"
        self._interest()
        self._fees()

    def __str__(self):
        """Formats the account number and balance of the account.
        For example, '#000000001,<tab>balance: $50.00'
        """
        return f"#{self._account_number:09},\tbalance: ${self.get_balance():,.2f}"

    def get_transactions(self):
        "Returns sorted list of transactions on this account"
        return sorted(self._transactions)


class SavingsAccount(Account):
    """Concrete Account class with daily and monthly account limits and high interest rate.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._interest_rate = Decimal("0.029")
        self._daily_limit = 2
        self._monthly_limit = 5

    def _check_limits(self, t1: Transaction) -> bool:
        """determines if the incoming trasaction is within the accounts transaction limits

        Args:
            t1 (Transaction): pending transaction to be checked

        Returns:
            bool: true if within limits and false if beyond limits
        """
        # Count number of non-exempt transactions on the same day as t1
        num_today = len(
            [t2 for t2 in self._transactions if not t2.is_exempt() and t2.in_same_day(t1)])
        if num_today >= self._daily_limit:
            raise TransactionLimitError(self._daily_limit, "day")

        # Count number of non-exempt transactions in the same month as t1
        num_this_month = len(
            [t2 for t2 in self._transactions if not t2.is_exempt() and t2.in_same_month(t1)])
        if num_this_month >= self._monthly_limit:
            raise TransactionLimitError(self._monthly_limit, "month")

        # check counts against daily and monthly limits
        return num_today < self._daily_limit and num_this_month < self._monthly_limit

    def __str__(self):
        """Formats the type, account number, and balance of the account.
        For example, 'Savings#000000001,<tab>balance: $50.00'
        """
        return "Savings" + super().__str__()


class CheckingAccount(Account):
    """Concrete Account class with lower interest rate and low balance fees.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._interest_rate = Decimal("0.0012")
        self._balance_threshold = 100
        self._low_balance_fee = -10

    def _fees(self):
        """Adds a low balance fee if balance is below a particular threshold. Fee amount and balance threshold are defined on the CheckingAccount.
        """
        if self.get_balance() < self._balance_threshold:
            latest_trans = self._find_latest_trans()
            latest_date = latest_trans._date
            t = Transaction(self._low_balance_fee, str(latest_date), exempt=True)
            self._transactions.append(t)
            logging.debug(f"Created transaction: {self._account_number}, {t._amt}")



    def __str__(self):
        """Formats the type, account number, and balance of the account.
        For example, 'Checking#000000001,<tab>balance: $50.00'
        """
        return "Checking" + super().__str__()
