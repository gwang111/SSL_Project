import sys
import socket
import multiprocessing

class Account:
    def __init__(self, name, pwd, publicKey, balance):
        self.name = name
        self.pwd = pwd
        self.publicKey = publicKey
        self.balance = balance
    
    def deposit(self, amount): self.balance += amount

    def withdraw(self, amount):
        if self.balance - amount >= 0: self.balance -= amount

    def checkBalance(self): print("[Banking Server] Account Balance For", self.name, "is", self.balance)

class Bank:
    def __init__(self) :
        self.data_base = [Account('Aayush', '1100011110', 'Sriram', 100000), 
                          Account('Aidan', '1101010111', 'Duane', 1000), 
                          Account('Gary', '1100010010', 'Wang', 100)]

class BankingServer:
    def __init__(self):
        self.bank = Bank()

    def startServer(self): 
        Running = True
        
        print('[Banking Server] Started...')
        while(Running):
            break    

def startup():
    server = BankingServer()
    server.startServer()

if __name__ == '__main__': startup()