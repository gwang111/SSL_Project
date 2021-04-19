import sys
import socket

class Account:
    def __init__(self, name, publicKey, balance):
        self.name = name
        self.publicKey = publicKey
        self.balance = balance
    
    def deposit(self, amount): self.balance += amount

    def withdraw(self, amount):
        if self.balance - amount >= 0: self.balance -= amount

    def checkBalance(self): print("[Banking Server] Account Balance For", self.name, "is", self.balance)

class Bank:
    def __init__(self) :
        self.data_base = [Account('Aayush', '1100011110', 100000), 
                          Account('Aidan', '1101010111', 1000), 
                          Account('Gary', '1100010010', 100)]

class BankingServer:
    def __init__(self):
        self.bank = Bank()

    def SSLHandShake(self): pass # <--- TODO

    def processRequests(self): pass # <--- TODO

    def openingServer(self): 
        # Establish listening from port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 10000)
        print('[Banking Server] Starting Up On:', server_address[0], 'Port:', server_address[1])
        sock.bind(server_address)
        sock.listen(1)
        
        # Wait for ATM To Connect
        while (True):

            # HandShake Protocol should happen here
            self.SSLHandShake() 

            # Below is just palaceholder code to confirm working message passing
            msg = ''

            print('[Banking Server] Waiting For Connection From ATM...')
            connection, client_address = sock.accept()   
            #connection.setblocking(0)
            try:
                while (True):
                    chunk = connection.recv(1024)
                    if (chunk and chunk.decode() != 'DONE'): msg += chunk.decode()
                    else: 
                        print('[Banking Server] Message Received')
                        send = '[From Banking Server] Received'
                        connection.sendall(send.encode())
                        connection.sendall('DONE'.encode())
                        msg = 'DONE'
                        break
            finally: connection.close()
            
            if (msg == 'DONE'): break

        # withdraw, deposit, check balance
        self.processRequests()

def startingUp():
    server = BankingServer()
    server.openingServer()
    print('[Banking Server] Shutting Down...')

if __name__ == '__main__': startingUp()