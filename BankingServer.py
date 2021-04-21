import sys
import socket
import BG
import DES
import RSA
import SHA1

pubKey = None

def recvMsg(connection):
    msg = ''
    try:
        while (True):
            chunk = connection.recv(1024)
            delim = chunk.decode().split()
            if delim[len(delim) - 1] != "End": msg += ' '.join(delim)
            else:
                msg += ' '.join(delim[:-1]) 
                break
    finally: return msg

def sendMsg(connection, msg):
    send_msg = msg + " End"
    connection.sendall(send_msg.encode()) 

class Account:
    def __init__(self, balance):
        self.balance = balance

    def deposit(self, amount): self.balance += amount

    def withdraw(self, amount):
        if self.balance - amount >= 0: self.balance -= amount

    def checkBalance(self): print("[Banking Server] Account Balance For Aayush is:", self.balance, "USD")

class Bank:
    def __init__(self) :
        self.aayush_account = Account(1000000)

class BankingServer:
    def __init__(self):
        self.bank = Bank()

    def SSLHandShake(self, sock):

        # Below is just palaceholder code to confirm working message passing
        msg = ''
        successful = True


        print('[Banking Server] Waiting For Connection From ATM...')
        connection, client_address = sock.accept()   
        
        # TODO https://piazza.com/class_profile/get_resource/kju77hlrkbr550/kmez90r3m4w5sn?
        # Phase 1
        ret = recvMsg(connection)
        sendMsg(connection, 'Hello_back')
        print("[Banking Server] Passed Phase 1")
        # Phase 2
        e,n,d,p = RSA.generateKeys()
        pub_key = (str(e) + ' ' + str(n))
        ret = recvMsg(connection)
        print(pub_key)
        sendMsg(connection, pub_key)
        print("[Banking Server] Passed Phase 2")
        # Phase 3
    
        ret = recvMsg(connection)
        dec_key = RSA.decrypt(ret,d,n)
        sendMsg(connection, 'Gotkey')
        print("[Banking Server] Passed Phase 3")
        # Phase 4
        ret = recvMsg(connection)

        if(RSA.decrypt(ret,dec_key,n) == 'clientPhase4'):
            print('Success')


        sendMsg(connection, 'Phase 4')
        print("[Banking Server] Passed Phase 4")

        return successful, connection

    def processRequests(self, connection): # <--- TODO
        # receive encrypted banking operations from ATM
        while (True):
            msg = recvMsg(connection)
            if msg == "Exit": break

            msg = msg.lower()
            msg = msg.split()    

            if msg[0] == 'w:': 
                print("[Banking Server] Processing Operation: " + ' '.join(msg))
                money = 0
                try:
                    money = int(msg[1])
                except:
                    print("[Banking Server] Invalid Amount")
                    continue
                self.bank.aayush_account.withdraw(int(msg[1]))
            elif msg[0] == 'd:': 
                print("[Banking Server] Processing Operation: " + ' '.join(msg))
                money = 0
                try:
                    money = int(msg[1])
                except:
                    print("[Banking Server] Invalid Amount")
                    continue                
                self.bank.aayush_account.deposit(int(msg[1]))
            elif msg[0] == 'cb': 
                print("[Banking Server] Processing Operation: " + msg[0])
                self.bank.aayush_account.checkBalance()
            elif msg[0] == 'e': break
            else: print("[Banking Server] Processing Operation Invalid")


    def openingServer(self): 
        # Establish listening from port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = ('localhost', 11111)
        print('[Banking Server] Starting Up On:', server_address[0], 'Port:', server_address[1])
        sock.bind(server_address)
        sock.listen(1)

        # HandShake Protocol should happen here
        successful, connection = self.SSLHandShake(sock) 

        if successful:
            print('[Banking Server] Handshake Protocol Success. Accepting Banking Operations')
            self.processRequests(connection)
        else:
            connection.close()
            print('[Banking Server] Handshake Protocol Failed. Exiting...')
            return
        connection.close()
        print('[Banking Server] Banking Operations Successful. Exiting...')


def startingUp():
    server = BankingServer()
    server.openingServer()
    print('[Banking Server] Shutting Down...')

if __name__ == '__main__': startingUp()
