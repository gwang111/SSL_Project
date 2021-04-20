import sys
import socket
import BG
import DES
import RSA
import SHA1

pubKey = None

class Account:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance

    def deposit(self, amount): self.balance += amount

    def withdraw(self, amount):
        if self.balance - amount >= 0: self.balance -= amount

    def checkBalance(self): print("[Banking Server] Account Balance For", self.name, "is", self.balance)

class Bank:
    def __init__(self) :
        self.data_base = Account('Aayush', 100000)

class BankingServer:
    def __init__(self):
        self.bank = Bank()

    def SSLHandShake(self, sock):

        # Below is just palaceholder code to confirm working message passing
        msg = ''
        successful = True

        print('[Banking Server] Waiting For Connection From ATM...')
        connection, client_address = sock.accept()   
        
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
        finally: return (successful, connection, sock)

        # TODO https://piazza.com/class_profile/get_resource/kju77hlrkbr550/kmez90r3m4w5sn?
        # Phase 1

        # Phase 2

        # Phase 3

        # Phase 4

    def processRequests(self, sock): pass # <--- TODO
        # receive encrypted banking operations from ATM

    def openingServer(self): 
        # Establish listening from port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = ('localhost', 11111)
        print('[Banking Server] Starting Up On:', server_address[0], 'Port:', server_address[1])
        sock.bind(server_address)
        sock.listen(1)

        # HandShake Protocol should happen here
        successful, connection, sock = self.SSLHandShake(sock) 

        if successful:
            self.processRequests(sock)
        else:
            connection.close()
            sock.close()
            print('[Banking Server] Handshake Protocol Failed. Exiting...')
            return
        connection.close()
        sock.close()
        print('[Banking Server] Banking Operations Successful. Exiting...')


def startingUp():
    server = BankingServer()
    server.openingServer()
    print('[Banking Server] Shutting Down...')

if __name__ == '__main__': startingUp()