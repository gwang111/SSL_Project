import sys
import socket
import BG
import DES
import RSA
import SHA1

pubKey = None
privKey = None

def recvMsg(sock):
    msg = ''
    try:
        while (True):
            chunk = sock.recv(1024)
            if (chunk and chunk.decode() != 'DONE'): msg += chunk.decode()
            else: break
    finally: return msg

def sendMsg(sock, msg):
    sock.sendall(msg.encode())
    sock.sendall('DONE'.encode())    

class ATM: 
    def __init__(self): pass

    def SSLHandShake(self, user_name, sock):
        successful = True
        # Below is just palaceholder code to confirm working message passing
        
        msg = 'DONE'
        sock.sendall(msg.encode())
        print('[ATM Client] Message Sent')

        try:
            recvMsg = ''
            while (True):
                chunk = sock.recv(1024)
                if (chunk and chunk.decode() != 'DONE'): recvMsg += chunk.decode()
                else:
                    print('[ATM Client] Message Received')
                    break
        finally: return successful

        # TODO https://piazza.com/class_profile/get_resource/kju77hlrkbr550/kmez90r3m4w5sn?
        # Phase 1

        # Phase 2

        # Phase 3

        # Phase 4

    def sendRequests(self, msg, sock): pass # <--- TODO
        # send encrypted banking operations to server

    def run(self, user_name):
        # Establish listening from port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 11111)
        print('[ATM Client] Connecting To:', server_address[0], "Port:", server_address[1])
        sock.connect(server_address)

        # HandShake Protocol should happen here
        successful = self.SSLHandShake(user_name, sock)

        if successful:
            # Banking Operations    
            # withdraw, deposit, check balance
            # Key:
            # w: 1,000 -> withdraw
            # d: 1,000 -> deposit
            # cb -> check balance
            # E -> Exit
            print('[ATM Client] Connection Accepted to Banking Server')
            while (True):
                req = input('[ATM Client] Enter Banking Operation: ')
                if req == "E": break
                self.sendRequests(req, sock)
        else:
            sock.close()
            print('[ATM Client] Handshake Protocol Failed. Exiting...')
            return
        sock.close()
        print('[ATM Client] Banking Operations Successful. Exiting...')


    def startATM(self):
        print('[ATM Client] Started...')
        while (True):
            login = input('[ATM Client] Enter YOUR_USER_NAME to Login, Type E to Exit: ')
            
            if (login == 'E'):
                print('[ATM Client] Shutting off ATM...')
                break
            else:
                print('[ATM Client] Connecting to Banking Server...')

                # Handshake Protocol + Banking Operations
                self.run(login)
                return


def startup():
    client = ATM()
    client.startATM()
    print('[ATM Client] Shutting Down...')

if __name__ == '__main__': startup()

