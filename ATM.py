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
            delim = chunk.decode().split()
            if delim[len(delim) - 1] != "End": msg += ' '.join(delim)
            else: 
                msg += ' '.join(delim[:-1])
                break
    finally: return msg

def sendMsg(sock, msg):
    send_msg = msg + " End"
    sock.sendall(send_msg.encode())

class ATM: 
    def __init__(self): pass

    def SSLHandShake(self, sock):
        successful = True

        # TODO https://piazza.com/class_profile/get_resource/kju77hlrkbr550/kmez90r3m4w5sn?
        # Phase 1
        sendMsg(sock, "Hello")
        ret = recvMsg(sock)
        print("[ATM Client] Passed Phase 1")
        # Phase 2
        sendMsg(sock, "Phase 2")
        ret = recvMsg(sock)
        e,n = ret.split()
        print("[ATM Client] Passed Phase 2")
        # Phase 3

        cypher = RSA('This is a A', e,n )


        sendMsg(sock, cypher)
        ret = recvMsg(sock)
        print("[ATM Client] Passed Phase 3")
        # Phase 4
        sendMsg(sock, "Phase 4")
        ret = recvMsg(sock)
        print("[ATM Client] Passed Phase 4")

        return successful

    def sendRequests(self, msg, sock): pass # <--- TODO
        # send encrypted banking operations to server

    def run(self):
        # Establish listening from port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 11111)
        print('[ATM Client] Connecting To:', server_address[0], "Port:", server_address[1])
        sock.connect(server_address)

        # HandShake Protocol should happen here
        successful = self.SSLHandShake(sock)

        if successful:
            # Banking Operations    
            # withdraw, deposit, check balance
            # Key:
            # w: 1000 -> withdraw
            # d: 1000 -> deposit
            # cb -> check balance
            # e -> Exit
            print('[ATM Client] Handshake Protocol Succeeded. Connection Accepted to Banking Server')
            while (True):
                req = input('[ATM Client] Enter Banking Operation: ')
                if req == "e": 
                    sendMsg(sock, req)
                    break
                sendMsg(sock, req)
        else:
            sock.close()
            print('[ATM Client] Handshake Protocol Failed. Denied Connection...')
            return
        sock.close()
        print('[ATM Client] Banking Operations Successful. Exiting...')


    def startATM(self):
        print('[ATM Client] Started...')
        while (True):
            op = input('[ATM Client] Type e to Exit, p to Proceed: ')
            
            if (op == 'e'):
                print('[ATM Client] Shutting off ATM...')
                break
            elif (op == 'p'):
                print('[ATM Client] Connecting to Banking Server...')

                # Handshake Protocol + Banking Operations
                self.run()
                return


def startup():
    client = ATM()
    client.startATM()
    print('[ATM Client] Shutting Down...')

if __name__ == '__main__': startup()

