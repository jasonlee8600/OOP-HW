from account import CheckingAccount, SavingsAccount

SAVINGS = "savings" 
CHECKING = "checking"

class Bank:
    """Top-level container/management class"""
    
    def __init__(self):
        self._accounts = []

    def new_account(self, account_type):
        """Creates a new account and adds it to the bank"""
        account_number = len(self._accounts) + 1
        if account_type == SAVINGS:
            account = SavingsAccount(account_number)
        elif account_type == CHECKING:   
            account = CheckingAccount(account_number)
        else:
            return None
        self._accounts.append(account)
        return account

    def select_account(self, account_number):
        """Returns account associated with queried account number to BankCLI"""
        for account in self._accounts:
            if account._account_number == account_number:
                return account
        return None
