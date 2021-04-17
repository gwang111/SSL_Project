import sys
import socket

class ATM: 
    def __init__(self): pass

    def start(self): pass

    def SSLHandShake(self): pass

    def establishConnection(self, user_name, pwd):
        # Establish listening from port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 10000)
        print('[ATM Client] Connecting To:', server_address[0], "Port:", server_address[1])
        sock.connect(server_address)

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
        finally: sock.close()

    def startATM(self):
        print('[ATM Client] Started...')
        while (True):
            login = input('[ATM Client] Enter YOUR_USER_NAME to Login, Type E to Exit: ')
            
            if (login == 'E'):
                print('[ATM Client] Shutting off ATM...')
                break
            else:
                print('[ATM Client] Connecting to Banking Server...')

                pwd = input('[ATM Client] Enter Your Password: ')
                self.establishConnection(login, pwd)

def startup():
    client = ATM()
    client.startATM()

if __name__ == '__main__': startup()

