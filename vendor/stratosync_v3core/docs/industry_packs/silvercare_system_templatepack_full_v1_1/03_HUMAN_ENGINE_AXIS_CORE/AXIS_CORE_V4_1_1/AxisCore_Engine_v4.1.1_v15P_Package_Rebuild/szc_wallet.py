class SZCWallet:
    def __init__(self, balance=0):
        self.balance = balance
    def send(self, amount):
        if amount <= self.balance:
            self.balance -= amount
            return True
        return False
    def receive(self, amount):
        self.balance += amount
