from datetime import datetime, date, timedelta
import logging
from decimal import setcontext, BasicContext
from base import Base
from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, Boolean


# context with ROUND_HALF_UP
setcontext(BasicContext)


class ComparableMixin():
    "Assumes that __lt__ is appropriately implemented and derives the remaining comparison methods from these"
    
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


class Transaction(ComparableMixin, Base):

    __tablename__ = "transaction"
    _id = Column(Integer, primary_key=True)
    _account_id = Column(Integer, ForeignKey('account._id'))
    _amt = Column(Numeric, primary_key=False)
    _date = Column(Date, primary_key=False)
    _exempt = Column(Boolean, primary_key=False)

    def __init__(self, amt, acct_num, date=None, exempt=False):
        """
        Args:
            amt (Decimal): Decimal object representing dollar amount of the transaction.
            acct_num (int): Account number used for logging the transaction's creation.
            date (Date, optional): Date object representing the date the transaction was created.Defaults to None.
            exempt (bool, optional): Determines whether the transaction is exempt from account limits. Defaults to False.
        """       
        self._amt = amt
        self._date = date
        if not self._date:
            self._date = datetime.now().date()

        self._exempt = exempt
        

    @property
    def date(self):
        # exposes the date as a read-only property to facilitate new
        # functionality in Account
        return self._date

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

    def last_day_of_month(self):
        "Returns a date corresponding to the last day in the same month as this transaction"
        
        # Creates a date on the first of the next month (being careful about
        # wrapping around to January) and then subtracts one day
        return date(self._date.year + self._date.month // 12, 
              self._date.month % 12 + 1, 1) - timedelta(1)
        


