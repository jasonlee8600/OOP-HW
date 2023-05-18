from decimal import Decimal
from datetime import datetime

class Account:
    """Base class for bank accounts. Maintains a list of transactions in the account.
methods support default behavior, but may be overridden by CheckingAccount and SavingsAccount"""
    def __init__(self, account_number):
        self._transactions = []
        self._account_number = account_number

    def __str__(self):
        """Prints account number and balance"""
        return f"#{str(self._account_number).zfill(9)},\tbalance: ${self.calc_balance():,.2f}"

    
    def add_transaction(self, transaction):
        """Adds a transaction to the Account's transactions list"""
        # check transaction limits
        if self._under_transaction_limit(transaction):
            self._transactions.append(transaction)

    def calc_balance(self):
        """Calculates an account's balance by adding up the transaction amounts"""
        total = 0
        for transaction in self._transactions:
            total += transaction._amount
        return total
    
    def interest(self):
        """Calculates interest based off of account balance and interest rate, then adds it as bypassed transaction"""
        # rounds (balance * interest_rate) to 2 decimal places before converting to Decimal() class
        transaction = Transaction(Decimal(round(self.calc_balance() * self._interest_rate, 2)), bypass=True)
        # immediately add to transactions list because ignores limits
        self._transactions.append(transaction)



class CheckingAccount(Account):
    """Accounts with less interest and fewer transaction limits"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._interest_rate = Decimal("0.0012")

    def __str__(self):
        """Just adds account type to Account's __str__ output"""
        return "Checking" + super().__str__()

    def _under_transaction_limit(self, transaction):
        """No transaction limit in Checking account so always returns true"""
        return True

    def fees(self):
        """Add -$10 fee if balance < 100 after applying interest"""
        if self.calc_balance() < 100:
            transaction = Transaction(Decimal(-10), bypass=True)
            # immediately add to transactions list because ignores limits
            self._transactions.append(transaction)



class SavingsAccount(Account):
    """Accounts with more interest and more transaction limits"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._interest_rate = Decimal("0.029")

    def __str__(self):
        """Just adds account type to Account's __str__ output"""
        return "Savings" + super().__str__()

    def _under_transaction_limit(self, transaction):
        """Checks if Savings account is under transaction limits (2 per day, 5 per month), ignoring interest/fees transactions (bypass=True)"""
        same_day = 0
        same_month = 0
        
        for t in self._transactions:
            # if same day and not an interest/fees transaction
            if t._date == transaction._date and transaction.bypass() == False:
                same_day += 1
            # if same month and year (index 0-6 since I stored date as a string in Transaction class)
            if t._date[0:6] == transaction._date[0:6] and transaction.bypass() == False:
                same_month += 1
        
        # 2 transactions is daily limit, 5 transactions is monthly limit
        if same_day < 2 and same_month < 5:
            return True
        else:
            return False
    
    def fees(self):
        """No fees for Savings accounts"""
        pass



class ComparableMixin:
    """Assumes that __lt__ is appropriately implemented and derives the remaining comparison methods from these"""
    def __ge__(self, other) -> bool:
        return not self.__lt__(other)
    def __gt__(self, other) -> bool:
        return other.__lt__(self)
    def __le__(self, other) -> bool:
        return not self.__gt__(other)
    def __eq__(self, other) -> bool:
        return not self.__lt__(other) and not self.__gt__(other)
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


class Transaction(ComparableMixin):
    """Transactions that store amount and date as attributes"""
    def __init__(self, amount, date=None, bypass=False):
        self._amount = Decimal(amount)
        if date == None:
            self._date = str(datetime.now().date())
        else:
            self._date = date 
        self._bypass = bypass

    def __str__(self):
        """Prints transaction date and amount"""
        return f"{self._date}, ${self._amount:,.2f}"

    def bypass(self):
        """Just returns transaction's bypass value
        True if interest/fees transaction, False if normal transaction"""
        return self._bypass

    def __lt__(self, other):
        """Allows sorting of Transaction objects by date"""
        return self._date < other._date