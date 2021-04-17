import sys
import socket
import multiprocessing

class ATM: 
    def __init__(self): pass

    def start(self): pass

    def establishConnection(self, user_name, pwd): pass

    def SSLHandShake(self): pass

    def startATM(self):
        running = True

        print('[ATM Client] Started...')
        while(running):
            login = input('\n[ATM Client] Enter YOUR_USER_NAME to Login, Type E to Exit: ')
            
            if (login == 'E'):
                print('\n[ATM Client] Shutting off ATM...')
                break
            else:
                print('\n[ATM Client] Connecting to Banking Server...')

                pwd = input('\n[ATM Client] Enter Your Password: ')
                self.establishConnection(login, pwd)

def startup():
    client = ATM()
    client.startATM()

if __name__ == '__main__': startup()

