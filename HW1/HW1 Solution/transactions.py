from datetime import datetime
from decimal import Decimal, setcontext, BasicContext
from comparable import ComparableMixin

# context with ROUND_HALF_UP
setcontext(BasicContext)

class Transaction(ComparableMixin):
    def __init__(self, amt, date=None, exempt=False):
        """
        Args:
            amt (string): String representing dollar amount of the transaction. Converted to Decimal.
            date (string, optional): Date string in the format YYYY-MM-DD. Defaults to None.
            exempt (bool, optional): Determines whether the transaction is exempt from account limits. Defaults to False.
        """        
        self._amt = Decimal(amt) # convert from string to Decimal to avoid rounding errors
        if date is None:
            self._date = datetime.now().date()
        else:
            self._date = datetime.strptime(date, "%Y-%m-%d").date()
        self._exempt = exempt

    def __str__(self):
        """Formats the date and amount of this transaction
        For example, 2022-9-15, $50.00'
        """ 
        return f"{self._date}, ${self._amt:,.2f}"

    def is_exempt(self):
        "Check if the transaction is exempt from account limits"
        return self._exempt

    def in_same_day(self, other):
        "Takes in a date object and checks whether this transaction shares the same date"
        return self._date == other._date

    def in_same_month(self, other):
        "Takes in a date object and checks whether this transaction shares the same month and year"
        return self._date.month == other._date.month and self._date.year == other._date.year

    def __radd__(self, other):
        "Adds Transactions by their amounts"

        # allows us to use sum() with transactions
        return other + self._amt

    def check_balance(self, balance):
        "Takes in an amount and checks whether this transaction would withdraw more than that amount"
        return self._amt >= 0 or balance >= abs(self._amt)

    def __lt__(self, value):
        "Compares Transactions by date"
        return self._date < value._date




